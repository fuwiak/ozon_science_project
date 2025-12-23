"""
Эндпоинты для интеграции с n8n
"""
from fastapi import APIRouter, HTTPException, Body
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import httpx
import os

router = APIRouter(prefix="/api/n8n", tags=["n8n"])


class N8NWorkflow(BaseModel):
    """Модель workflow n8n"""
    id: str
    name: str
    active: bool
    nodes: int = Field(..., description="Количество узлов в workflow")
    lastExecuted: Optional[str] = Field(None, description="Дата последнего выполнения")


class N8NWorkflowListResponse(BaseModel):
    """Ответ со списком workflows"""
    workflows: List[N8NWorkflow]
    total: int


class N8NConnectionSettings(BaseModel):
    """Настройки подключения к n8n"""
    url: str = Field(..., description="URL n8n инстанса")
    api_key: str = Field(..., description="API ключ для n8n")


class N8NWorkflowToggle(BaseModel):
    """Запрос на переключение статуса workflow"""
    workflow_id: str
    active: bool


def get_n8n_client(url: str, api_key: str) -> httpx.AsyncClient:
    """Создает клиент для работы с n8n API"""
    return httpx.AsyncClient(
        base_url=url,
        headers={
            "X-N8N-API-KEY": api_key,
            "Content-Type": "application/json",
        },
        timeout=10.0
    )


@router.get("/workflows", response_model=N8NWorkflowListResponse)
async def get_workflows(
    url: Optional[str] = None,
    api_key: Optional[str] = None
):
    """
    Получает список workflows из n8n
    
    Если url и api_key не указаны, возвращает моковые данные
    """
    # Если параметры не указаны, используем переменные окружения
    if not url:
        url = os.getenv("N8N_URL", "")
    if not api_key:
        api_key = os.getenv("N8N_API_KEY", "")
    
    # Если нет настроек, возвращаем моковые данные
    if not url or not api_key:
        return get_mock_workflows()
    
    try:
        async with get_n8n_client(url, api_key) as client:
            response = await client.get("/api/v1/workflows")
            
            if response.status_code == 200:
                data = response.json()
                workflows_data = data.get("data", [])
                
                workflows = []
                for wf in workflows_data:
                    workflows.append(N8NWorkflow(
                        id=str(wf.get("id", "")),
                        name=wf.get("name", "Unnamed"),
                        active=wf.get("active", False),
                        nodes=len(wf.get("nodes", [])),
                        lastExecuted=wf.get("updatedAt")
                    ))
                
                return N8NWorkflowListResponse(
                    workflows=workflows,
                    total=len(workflows)
                )
            else:
                # При ошибке возвращаем моковые данные
                return get_mock_workflows()
                
    except Exception as e:
        # При любой ошибке возвращаем моковые данные
        print(f"Ошибка подключения к n8n: {e}")
        return get_mock_workflows()


def get_mock_workflows() -> N8NWorkflowListResponse:
    """Возвращает моковые workflows"""
    from datetime import datetime, timedelta
    
    workflows = [
        N8NWorkflow(
            id="1",
            name="Обновление цен на основе спроса",
            active=True,
            nodes=5,
            lastExecuted=(datetime.now() - timedelta(hours=2)).isoformat()
        ),
        N8NWorkflow(
            id="2",
            name="Мониторинг остатков на складе",
            active=False,
            nodes=8,
            lastExecuted=(datetime.now() - timedelta(days=1)).isoformat()
        ),
        N8NWorkflow(
            id="3",
            name="Анализ цен конкурентов",
            active=True,
            nodes=12,
            lastExecuted=(datetime.now() - timedelta(minutes=30)).isoformat()
        ),
        N8NWorkflow(
            id="4",
            name="Автоматическое пополнение товаров",
            active=True,
            nodes=15,
            lastExecuted=(datetime.now() - timedelta(hours=5)).isoformat()
        ),
        N8NWorkflow(
            id="5",
            name="Уведомления о критичных остатках",
            active=True,
            nodes=6,
            lastExecuted=(datetime.now() - timedelta(hours=1)).isoformat()
        ),
        N8NWorkflow(
            id="6",
            name="Экспорт данных для аналитики",
            active=False,
            nodes=4,
            lastExecuted=(datetime.now() - timedelta(days=3)).isoformat()
        ),
    ]
    
    return N8NWorkflowListResponse(
        workflows=workflows,
        total=len(workflows)
    )


@router.post("/workflows/{workflow_id}/toggle")
async def toggle_workflow(
    workflow_id: str,
    active: bool = Body(..., embed=True),
    url: Optional[str] = None,
    api_key: Optional[str] = None
):
    """
    Переключает статус workflow (активен/неактивен)
    """
    # Если параметры не указаны, используем переменные окружения
    if not url:
        url = os.getenv("N8N_URL", "")
    if not api_key:
        api_key = os.getenv("N8N_API_KEY", "")
    
    if not url or not api_key:
        # Если нет настроек, просто возвращаем успех (для моковых данных)
        return {"success": True, "message": "Workflow status toggled (mock mode)"}
    
    try:
        async with get_n8n_client(url, api_key) as client:
            # Активируем или деактивируем workflow
            endpoint = f"/api/v1/workflows/{workflow_id}/activate" if active else f"/api/v1/workflows/{workflow_id}/deactivate"
            response = await client.post(endpoint)
            
            if response.status_code in [200, 201]:
                return {"success": True, "message": f"Workflow {'activated' if active else 'deactivated'}"}
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Ошибка при переключении workflow: {response.text}"
                )
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Ошибка подключения к n8n: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")


@router.post("/workflows/{workflow_id}/execute")
async def execute_workflow(
    workflow_id: str,
    url: Optional[str] = None,
    api_key: Optional[str] = None,
    data: Optional[Dict[str, Any]] = Body(None)
):
    """
    Запускает workflow вручную
    """
    # Если параметры не указаны, используем переменные окружения
    if not url:
        url = os.getenv("N8N_URL", "")
    if not api_key:
        api_key = os.getenv("N8N_API_KEY", "")
    
    if not url or not api_key:
        # Если нет настроек, просто возвращаем успех (для моковых данных)
        return {"success": True, "message": "Workflow executed (mock mode)", "execution_id": "mock-123"}
    
    try:
        async with get_n8n_client(url, api_key) as client:
            # Запускаем workflow через webhook или API
            response = await client.post(
                f"/api/v1/workflows/{workflow_id}/execute",
                json=data or {}
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                return {
                    "success": True,
                    "message": "Workflow executed",
                    "execution_id": result.get("id", "unknown")
                }
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Ошибка при запуске workflow: {response.text}"
                )
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Ошибка подключения к n8n: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")


@router.get("/workflows/{workflow_id}")
async def get_workflow(
    workflow_id: str,
    url: Optional[str] = None,
    api_key: Optional[str] = None
):
    """
    Получает детальную информацию о workflow
    """
    # Если параметры не указаны, используем переменные окружения
    if not url:
        url = os.getenv("N8N_URL", "")
    if not api_key:
        api_key = os.getenv("N8N_API_KEY", "")
    
    if not url or not api_key:
        # Возвращаем моковые данные
        mock_workflows = get_mock_workflows()
        workflow = next((w for w in mock_workflows.workflows if w.id == workflow_id), None)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        return workflow
    
    try:
        async with get_n8n_client(url, api_key) as client:
            response = await client.get(f"/api/v1/workflows/{workflow_id}")
            
            if response.status_code == 200:
                wf = response.json()
                return N8NWorkflow(
                    id=str(wf.get("id", "")),
                    name=wf.get("name", "Unnamed"),
                    active=wf.get("active", False),
                    nodes=len(wf.get("nodes", [])),
                    lastExecuted=wf.get("updatedAt")
                )
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Ошибка при получении workflow: {response.text}"
                )
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Ошибка подключения к n8n: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")


@router.post("/test-connection")
async def test_connection(
    settings: N8NConnectionSettings
):
    """
    Тестирует подключение к n8n
    """
    try:
        async with get_n8n_client(settings.url, settings.api_key) as client:
            response = await client.get("/api/v1/workflows?limit=1")
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "Подключение успешно",
                    "workflows_count": len(response.json().get("data", []))
                }
            else:
                return {
                    "success": False,
                    "message": f"Ошибка подключения: {response.status_code}",
                    "error": response.text
                }
    except Exception as e:
        return {
            "success": False,
            "message": f"Ошибка подключения: {str(e)}"
        }



