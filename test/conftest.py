import base64
import json
import os
from packaging.version import Version
import shutil
import socket
import subprocess
import time
import uuid

import pytest

from . import docker
from . import client
from ddapm_test_agent.client import TestAgentClient


@pytest.fixture(scope="session")
def log_dir(tmp_path_factory):
    return tmp_path_factory.mktemp("logs")


@pytest.fixture(scope="session")
def docker_network_name():
    return f"llmobs-test-{str(uuid.uuid4())[0:8]}"


@pytest.fixture(scope="session")
def docker_network(docker_network_name):
    docker = shutil.which("docker")
    subprocess.run([docker, "network", "create", docker_network_name], check=True)
    yield docker_network_name
    subprocess.run([docker, "network", "rm", docker_network_name], check=True)


@pytest.fixture(scope="session", autouse=True)
def ensure_docker_running() -> None:
    if not docker.running():
        pytest.fail("Docker is not running. Please start Docker and re-run the tests.")


@pytest.fixture(params=os.environ.get("TEST_LIBS", "python,nodejs").split(","))
def test_lang(request):
    assert request.param in [
        "python",
        "nodejs",
    ], f"Invalid test language '{request.param}' provided"
    return request.param


def _find_port() -> int:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))  # Bind to a free port provided by the host.
    port = s.getsockname()[1]  # Get the port number assigned.
    s.close()  # Release the socket.
    # assume nothing else grabs the port 🤞
    return port


@pytest.fixture(scope="session")
def testagent_port():
    return _find_port()


@pytest.fixture(scope="session")
def testagent_docker_name():
    return "mlobs-test-agent"


class LLMObsTestAgentClient(TestAgentClient):
    """Extend TestAgentClient to provide additional functionality for LLMObs."""

    def wait_for_llmobs_requests(self, num):
        """Wait for `num` llmobs requests to be received from the test agent."""
        num_received = 0
        while num_received < num:
            reqs = self.llmobs_requests()
            num_received = len(reqs)
            if num_received < num:
                time.sleep(0.1)
        return reqs

    def llmobs_requests(self):
        reqs = [
            r
            for r in self.requests()
            if r["url"].endswith("/evp_proxy/v2/api/v2/llmobs")
        ]
        return [json.loads(base64.b64decode(r["body"])) for r in reqs]


@pytest.fixture(scope="session")
def _test_agent(docker_network, testagent_docker_name, testagent_port):
    """
    Run a test agent for the duration of the test session.

    The test agent listens on both a TCP port and a UDS socket so both can be tested.

    A client is returned to interact with the test agent.
    """
    docker_args = dict(
        image="ghcr.io/datadog/dd-apm-test-agent/ddapm-test-agent:latest",
        environment={
            "PORT": testagent_port,
        },
        ports={testagent_port: testagent_port},
        name=testagent_docker_name,
        network=docker_network,
        volumes=[],
    )

    c = docker.docker_run(**docker_args, detach=True)
    try:
        agent = LLMObsTestAgentClient(base_url=f"http://localhost:{testagent_port}")
        try:
            # Wait for the agent to start
            agent.wait_to_start(num_tries=10, delay=0.1)
        except Exception as e:
            # If the container did start but the agent isn't working then get the logs and reraise.
            if c.is_running():
                raise Exception(
                    f"test agent container started but agent not responsive:\n\n{e}"
                ) from None

            # If the container didn't start then likely there was a bad test agent config in which case
            # we can try to run the container synchronously to get the logs.
            stdout, stderr = docker.docker_run(**docker_args, detach=False)
            raise Exception(
                f"test agent container failed to start, container stderr:\n\n{stderr.decode()}"
            ) from None

        yield agent
    finally:
        if c.is_running():
            c.kill()


@pytest.fixture(scope="function")
def test_agent(_test_agent):
    """
    We run the test agent once for the entirety of the test suite. So in order to not have conflicts between test cases
    the test agent state is cleared between runs.
    """
    _test_agent.clear()
    yield _test_agent
    _test_agent.clear()


@pytest.fixture
def test_client(
    request, docker_network, test_lang, testagent_docker_name, testagent_port
):
    curdir = os.path.dirname(os.path.abspath(__file__))
    docker.docker_build(
        f"llmobs-test-server-{test_lang}",
        dockerfile=os.path.join(curdir, f"Dockerfile.{test_lang}"),
        context=curdir,
    )

    local_port = str(_find_port())
    internal_port = "8080"
    container = docker.docker_run(
        image=f"llmobs-test-server-{test_lang}",
        detach=True,
        ports={local_port: internal_port},
        network=docker_network,
        environment={
            "PORT": internal_port,
            "DD_TRACE_AGENT_URL": f"http://{testagent_docker_name}:{testagent_port}",
            "DD_TRACE_DEBUG": "true",
            "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY"),
        },
        volumes=[],
    )
    try:
        c = client.InstrumentationClient(
            f"http://0.0.0.0:{local_port}", test_lang=test_lang
        )
        server_info = c.wait_to_start()

        # Confirm that the test case is compatible with the server
        lib_support = getattr(request.node.function, "library_support", [])
        for lang, version, reason in lib_support:
            if lang == test_lang:
                if version == "unsupported":
                    pytest.skip(f"Test does not support {test_lang}, reason: {reason}")
                if Version(server_info["version"]) < Version(version):
                    pytest.skip(
                        f"Test does not support {test_lang} {version}, min version is '{version}'"
                    )
        yield c
        print(container.logs(stderr=True, stdout=False))
        print(container.logs(stdout=True))
    finally:
        container.kill()
