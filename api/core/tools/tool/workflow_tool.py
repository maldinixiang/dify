import json
from copy import deepcopy
from typing import Any, Union

from flask_login import current_user

from core.app.apps.workflow.app_generator import WorkflowAppGenerator
from core.tools.entities.tool_entities import ToolInvokeMessage, ToolProviderType
from core.tools.tool.tool import Tool


class WorkflowTool(Tool):
    workflow_app_id: str
    workflow_entities: dict[str, Any]
    workflow_call_depth: int

    """
    Workflow tool.
    """
    def tool_provider_type(self) -> ToolProviderType:
        """
            get the tool provider type

            :return: the tool provider type
        """
        return ToolProviderType.WORKFLOW_BASED
    
    def _invoke(self, user_id: str, tool_parameters: dict[str, Any]) \
        -> Union[ToolInvokeMessage, list[ToolInvokeMessage]]:
        """
            invoke the tool
        """
        workflow = self.workflow_entities.get('workflow')
        app = self.workflow_entities.get('app')
        if not workflow or not app:
            raise ValueError('workflow not found')
        
        generator = WorkflowAppGenerator()
        result = generator.generate(
            app_model=app, 
            workflow=workflow, 
            user=current_user, 
            args=tool_parameters, 
            invoke_from=self.runtime.invoke_from,
            stream=False,
            call_depth=self.workflow_call_depth
        )

        return self.create_text_message(json.dumps(result))

    def fork_tool_runtime(self, meta: dict[str, Any]) -> 'WorkflowTool':
        """
            fork a new tool with meta data

            :param meta: the meta data of a tool call processing, tenant_id is required
            :return: the new tool
        """
        return self.__class__(
            identity=deepcopy(self.identity),
            parameters=deepcopy(self.parameters),
            description=deepcopy(self.description),
            runtime=Tool.Runtime(**meta),
            workflow_app_id=self.workflow_app_id,
            workflow_entities=deepcopy(self.workflow_entities)
        )