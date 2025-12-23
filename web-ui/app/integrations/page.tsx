'use client';

import { useEffect, useState } from 'react';
import { Workflow, Zap, Settings, Play, Pause, RefreshCw, Bot, Send, CheckCircle, XCircle } from 'lucide-react';
import { api } from '@/lib/api';

interface N8NWorkflow {
  id: string;
  name: string;
  active: boolean;
  nodes: number;
  lastExecuted?: string;
}

export default function IntegrationsPage() {
  const [workflows, setWorkflows] = useState<N8NWorkflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [n8nUrl, setN8nUrl] = useState<string>('');
  const [n8nApiKey, setN8nApiKey] = useState<string>('');
  
  // Telegram настройки
  const [telegramBotToken, setTelegramBotToken] = useState<string>('');
  const [telegramWebhookUrl, setTelegramWebhookUrl] = useState<string>('');
  const [telegramStatus, setTelegramStatus] = useState<any>(null);
  const [telegramLoading, setTelegramLoading] = useState(false);
  const [testChatId, setTestChatId] = useState<string>('');
  const [testMessage, setTestMessage] = useState<string>('');

  useEffect(() => {
    // Загружаем сохраненные настройки
    const savedUrl = localStorage.getItem('n8n_url') || '';
    const savedApiKey = localStorage.getItem('n8n_api_key') || '';
    setN8nUrl(savedUrl);
    setN8nApiKey(savedApiKey);

    if (savedUrl && savedApiKey) {
      fetchWorkflows(savedUrl, savedApiKey);
    } else {
      // Показываем моковые данные по умолчанию
      setWorkflows(getMockWorkflows());
      setLoading(false);
    }

    // Загружаем статус Telegram бота
    loadTelegramStatus();
  }, []);

  const loadTelegramStatus = async () => {
    try {
      const status = await api.getTelegramBotStatus();
      setTelegramStatus(status);
      if (status.configured && status.bot_username) {
        // Загружаем сохраненный токен из localStorage (если есть)
        const savedToken = localStorage.getItem('telegram_bot_token') || '';
        setTelegramBotToken(savedToken);
      }
    } catch (error) {
      console.error('Ошибка загрузки статуса Telegram:', error);
    }
  };

  const getMockWorkflows = (): N8NWorkflow[] => {
    return [
      {
        id: '1',
        name: 'Обновление цен на основе спроса',
        active: true,
        nodes: 5,
        lastExecuted: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: '2',
        name: 'Мониторинг остатков на складе',
        active: false,
        nodes: 8,
        lastExecuted: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: '3',
        name: 'Анализ цен конкурентов',
        active: true,
        nodes: 12,
        lastExecuted: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
      },
      {
        id: '4',
        name: 'Автоматическое пополнение товаров',
        active: true,
        nodes: 15,
        lastExecuted: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: '5',
        name: 'Уведомления о критичных остатках',
        active: true,
        nodes: 6,
        lastExecuted: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: '6',
        name: 'Экспорт данных для аналитики',
        active: false,
        nodes: 4,
        lastExecuted: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
      },
    ];
  };

  const fetchWorkflows = async (url: string, apiKey: string) => {
    try {
      setLoading(true);
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/n8n/workflows?url=${encodeURIComponent(url)}&api_key=${encodeURIComponent(apiKey)}`);

      if (response.ok) {
        const data = await response.json();
        const workflowsList = data.workflows || [];
        setWorkflows(workflowsList.map((wf: any) => ({
          id: wf.id,
          name: wf.name,
          active: wf.active,
          nodes: wf.nodes,
          lastExecuted: wf.lastExecuted || wf.last_executed,
        })));
      } else {
        console.error('Ошибка загрузки workflows');
        setWorkflows(getMockWorkflows());
      }
    } catch (error) {
      console.error('Ошибка подключения к n8n:', error);
      setWorkflows(getMockWorkflows());
    } finally {
      setLoading(false);
    }
  };

  const handleSaveSettings = async () => {
    localStorage.setItem('n8n_url', n8nUrl);
    localStorage.setItem('n8n_api_key', n8nApiKey);
    if (n8nUrl && n8nApiKey) {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const testResponse = await fetch(`${apiUrl}/api/n8n/test-connection`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ url: n8nUrl, api_key: n8nApiKey }),
        });
        
        const testResult = await testResponse.json();
        if (testResult.success) {
          alert('Настройки сохранены и подключение успешно!');
          fetchWorkflows(n8nUrl, n8nApiKey);
        } else {
          alert(`Настройки сохранены, но подключение не удалось: ${testResult.message}`);
          fetchWorkflows(n8nUrl, n8nApiKey);
        }
      } catch (error) {
        alert('Настройки сохранены, но не удалось проверить подключение');
        fetchWorkflows(n8nUrl, n8nApiKey);
      }
    } else {
      alert('Настройки сохранены');
      setWorkflows(getMockWorkflows());
    }
  };

  const handleSaveTelegramSettings = async () => {
    try {
      setTelegramLoading(true);
      const result = await api.saveTelegramBotSettings(telegramBotToken, telegramWebhookUrl || undefined);
      
      if (result.success) {
        localStorage.setItem('telegram_bot_token', telegramBotToken);
        alert(`Настройки Telegram бота сохранены! Бот: @${result.bot_username}`);
        await loadTelegramStatus();
      } else {
        alert(`Ошибка: ${result.message || 'Неизвестная ошибка'}`);
      }
    } catch (error: any) {
      alert(`Ошибка сохранения настроек: ${error.response?.data?.detail || error.message || 'Неизвестная ошибка'}`);
    } finally {
      setTelegramLoading(false);
    }
  };

  const handleSendTestMessage = async () => {
    if (!testChatId || !testMessage) {
      alert('Заполните Chat ID и сообщение');
      return;
    }

    try {
      setTelegramLoading(true);
      const result = await api.sendTelegramMessage(testChatId, testMessage);
      if (result.success) {
        alert('Сообщение отправлено успешно!');
        setTestMessage('');
      } else {
        alert(`Ошибка отправки: ${result.message || 'Неизвестная ошибка'}`);
      }
    } catch (error: any) {
      alert(`Ошибка отправки сообщения: ${error.response?.data?.detail || error.message || 'Неизвестная ошибка'}`);
    } finally {
      setTelegramLoading(false);
    }
  };

  const handleSetTelegramMenu = async () => {
    try {
      setTelegramLoading(true);
      const result = await api.setTelegramMenu();
      if (result.success) {
        alert('Меню установлено успешно!');
      } else {
        alert(`Ошибка: ${result.message || 'Неизвестная ошибка'}`);
      }
    } catch (error: any) {
      alert(`Ошибка установки меню: ${error.response?.data?.detail || error.message || 'Неизвестная ошибка'}`);
    } finally {
      setTelegramLoading(false);
    }
  };

  const toggleWorkflow = async (workflowId: string, active: boolean) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const url = n8nUrl || '';
      const apiKey = n8nApiKey || '';
      
      if (url && apiKey) {
        const response = await fetch(
          `${apiUrl}/api/n8n/workflows/${workflowId}/toggle?url=${encodeURIComponent(url)}&api_key=${encodeURIComponent(apiKey)}`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ active: !active }),
          }
        );
        
        if (response.ok) {
          setWorkflows(workflows.map(w => 
            w.id === workflowId ? { ...w, active: !active } : w
          ));
        }
      } else {
        setWorkflows(workflows.map(w => 
          w.id === workflowId ? { ...w, active: !active } : w
        ));
      }
    } catch (error) {
      console.error('Ошибка переключения workflow:', error);
      setWorkflows(workflows.map(w => 
        w.id === workflowId ? { ...w, active: !active } : w
      ));
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Никогда';
    return new Date(dateString).toLocaleString('ru-RU');
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8 fade-in">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-[#005BFF] to-[#00D9FF] bg-clip-text text-transparent">
          Интеграции
        </h1>
        <p className="mt-3 text-lg text-gray-600">
          Управление интеграциями: n8n workflows и Telegram бот
        </p>
      </div>

      {/* Telegram Bot настройки */}
      <div className="card p-6 mb-8">
        <div className="flex items-center mb-4">
          <Bot className="h-6 w-6 text-[#005BFF] mr-2" />
          <h2 className="text-2xl font-bold text-gray-800">Telegram Bot</h2>
        </div>

        {telegramStatus && (
          <div className={`mb-4 p-4 rounded-lg ${
            telegramStatus.configured 
              ? 'bg-green-50 border border-green-200' 
              : 'bg-yellow-50 border border-yellow-200'
          }`}>
            <div className="flex items-center">
              {telegramStatus.configured ? (
                <CheckCircle className="h-5 w-5 text-green-600 mr-2" />
              ) : (
                <XCircle className="h-5 w-5 text-yellow-600 mr-2" />
              )}
              <div>
                <p className={`text-sm font-medium ${
                  telegramStatus.configured ? 'text-green-800' : 'text-yellow-800'
                }`}>
                  {telegramStatus.configured 
                    ? `Бот @${telegramStatus.bot_username} настроен` 
                    : 'Telegram бот не настроен'}
                </p>
                {telegramStatus.webhook_url && (
                  <p className="text-xs text-gray-600 mt-1">
                    Webhook: {telegramStatus.webhook_url}
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Токен Telegram бота *
            </label>
            <input
              type="password"
              value={telegramBotToken}
              onChange={(e) => setTelegramBotToken(e.target.value)}
              placeholder="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#005BFF] focus:border-transparent"
            />
            <p className="text-xs text-gray-500 mt-1">
              Получите токен у @BotFather в Telegram
            </p>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Webhook URL (опционально)
            </label>
            <input
              type="url"
              value={telegramWebhookUrl}
              onChange={(e) => setTelegramWebhookUrl(e.target.value)}
              placeholder="https://your-domain.com/api/telegram/webhook"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#005BFF] focus:border-transparent"
            />
            <p className="text-xs text-gray-500 mt-1">
              URL для получения сообщений от Telegram (через n8n или напрямую)
            </p>
          </div>
          
          <div className="flex space-x-2">
            <button
              onClick={handleSaveTelegramSettings}
              disabled={telegramLoading || !telegramBotToken}
              className="px-6 py-2 bg-gradient-to-r from-[#005BFF] to-[#00D9FF] text-white rounded-lg font-semibold hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {telegramLoading ? 'Сохранение...' : 'Сохранить настройки'}
            </button>
            <button
              onClick={handleSetTelegramMenu}
              disabled={telegramLoading || !telegramStatus?.configured}
              className="px-6 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Установить меню
            </button>
            <button
              onClick={loadTelegramStatus}
              disabled={telegramLoading}
              className="px-6 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors disabled:opacity-50"
            >
              <RefreshCw className="h-4 w-4 inline mr-2" />
              Обновить статус
            </button>
          </div>
        </div>

        {/* Тестовая отправка сообщения */}
        {telegramStatus?.configured && (
          <div className="mt-6 pt-6 border-t border-gray-200">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Тестовая отправка сообщения</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Chat ID
                </label>
                <input
                  type="text"
                  value={testChatId}
                  onChange={(e) => setTestChatId(e.target.value)}
                  placeholder="123456789"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#005BFF] focus:border-transparent"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Ваш Telegram Chat ID (можно получить у @userinfobot)
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Сообщение
                </label>
                <textarea
                  value={testMessage}
                  onChange={(e) => setTestMessage(e.target.value)}
                  placeholder="Тестовое сообщение"
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#005BFF] focus:border-transparent"
                />
              </div>
              <button
                onClick={handleSendTestMessage}
                disabled={telegramLoading || !testChatId || !testMessage}
                className="flex items-center px-6 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Send className="h-4 w-4 mr-2" />
                Отправить сообщение
              </button>
            </div>
          </div>
        )}
      </div>

      {/* n8n настройки */}
      <div className="card p-6 mb-8">
        <div className="flex items-center mb-4">
          <Settings className="h-6 w-6 text-[#005BFF] mr-2" />
          <h2 className="text-2xl font-bold text-gray-800">Настройки подключения n8n</h2>
        </div>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              URL n8n инстанса
            </label>
            <input
              type="text"
              value={n8nUrl}
              onChange={(e) => setN8nUrl(e.target.value)}
              placeholder="https://n8n.example.com"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#005BFF] focus:border-transparent"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              API Key
            </label>
            <input
              type="password"
              value={n8nApiKey}
              onChange={(e) => setN8nApiKey(e.target.value)}
              placeholder="Введите API ключ"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#005BFF] focus:border-transparent"
            />
          </div>
          
          <button
            onClick={handleSaveSettings}
            className="px-6 py-2 bg-gradient-to-r from-[#005BFF] to-[#00D9FF] text-white rounded-lg font-semibold hover:shadow-lg transition-all"
          >
            Сохранить настройки
          </button>
        </div>
      </div>

      {/* Список workflows */}
      <div className="card p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center">
            <Workflow className="h-6 w-6 text-[#005BFF] mr-2" />
            <h2 className="text-2xl font-bold text-gray-800">n8n Workflows</h2>
          </div>
          <button
            onClick={() => {
              if (n8nUrl && n8nApiKey) {
                fetchWorkflows(n8nUrl, n8nApiKey);
              } else {
                setWorkflows(getMockWorkflows());
                setLoading(false);
              }
            }}
            className="flex items-center px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Обновить
          </button>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#005BFF] mx-auto"></div>
            <p className="mt-4 text-gray-600">Загрузка workflows...</p>
          </div>
        ) : (
          <div className="space-y-4">
            {workflows.map((workflow) => (
              <div
                key={workflow.id}
                className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center mb-2">
                      <h3 className="text-lg font-semibold text-gray-800 mr-3">
                        {workflow.name}
                      </h3>
                      <span
                        className={`px-2 py-1 rounded text-xs font-medium ${
                          workflow.active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {workflow.active ? 'Активен' : 'Неактивен'}
                      </span>
                    </div>
                    <div className="flex items-center text-sm text-gray-600 space-x-4">
                      <span className="flex items-center">
                        <Zap className="h-4 w-4 mr-1" />
                        {workflow.nodes} узлов
                      </span>
                      <span>Последний запуск: {formatDate(workflow.lastExecuted)}</span>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => toggleWorkflow(workflow.id, workflow.active)}
                      className={`p-2 rounded-lg transition-colors ${
                        workflow.active
                          ? 'bg-red-100 text-red-600 hover:bg-red-200'
                          : 'bg-green-100 text-green-600 hover:bg-green-200'
                      }`}
                      title={workflow.active ? 'Остановить' : 'Запустить'}
                    >
                      {workflow.active ? (
                        <Pause className="h-5 w-5" />
                      ) : (
                        <Play className="h-5 w-5" />
                      )}
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
