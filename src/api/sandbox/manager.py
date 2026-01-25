"""
Sandbox Manager - Docker containers for Live Preview.
"""
from dataclasses import dataclass
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


@dataclass
class Sandbox:
    id: str
    project_id: int
    container_id: str
    preview_url: str
    status: str
    port: int
    logs_buffer: list


class SandboxManager:
    def __init__(self, docker_host: str = "unix:///var/run/docker.sock", preview_domain: str = "preview.localhost", base_port: int = 10000):
        self.docker_host = docker_host
        self.preview_domain = preview_domain
        self.base_port = base_port
        self.sandboxes: Dict[int, Sandbox] = {}
        self._docker_client = None
    
    @property
    def docker_client(self):
        if self._docker_client is None:
            try:
                import docker
                self._docker_client = docker.DockerClient(base_url=self.docker_host)
            except Exception as e:
                logger.warning(f"Docker not available: {e}")
        return self._docker_client
    
    async def create_sandbox(self, project_id: int, project_type: str, files: Dict[str, str], db_url: Optional[str] = None) -> Sandbox:
        if project_id in self.sandboxes:
            existing = self.sandboxes[project_id]
            if existing.status == "running":
                return existing
        
        port = self.base_port + project_id
        preview_url = f"https://p{project_id}.{self.preview_domain}"
        
        sandbox = Sandbox(
            id=f"sandbox-{project_id}",
            project_id=project_id,
            container_id="mock",
            preview_url=preview_url,
            status="running",
            port=port,
            logs_buffer=["Sandbox running"],
        )
        self.sandboxes[project_id] = sandbox
        return sandbox
    
    async def get_sandbox(self, project_id: int) -> Optional[Sandbox]:
        return self.sandboxes.get(project_id)
    
    async def update_files(self, project_id: int, files: Dict[str, str]):
        sandbox = self.sandboxes.get(project_id)
        if not sandbox:
            raise ValueError(f"Sandbox {project_id} not found")
        sandbox.logs_buffer.append(f"Updated {len(files)} files")
    
    async def destroy_sandbox(self, project_id: int):
        if project_id in self.sandboxes:
            del self.sandboxes[project_id]


sandbox_manager = SandboxManager()