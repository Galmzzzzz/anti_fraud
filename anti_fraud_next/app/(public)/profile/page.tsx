'use client'

import { useEffect, useState } from 'react'
import axios from 'axios'

interface Transaction {
  id: number
  sender_id: number
  receiver_id: number
  sum: number
  status: string
  is_fraud: boolean
  device_id: number | null
  user_ip: string
  direction: 'sent' | 'received'
}

interface Device {
  device_id: number
  device: string
  user_ip: string
  screen_width: number
  screen_height: number
}

interface User {
  id: number
  phone_number: string
  balance: number
  country: string
  ip: string
  devices: Device[]
}

export default function ProfilePage() {
  const [user, setUser] = useState<User | null>(null)
  const [transactions, setTransactions] = useState<Transaction[]>([])

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [userRes, transactionsRes] = await Promise.all([
          axios.get('http://localhost:8000/me', { withCredentials: true }),
          axios.get('http://localhost:8000/get_transactions', { withCredentials: true }),
        ])
        setUser(userRes.data)
        setTransactions(transactionsRes.data)
      } catch (err) {
        console.error(err)
      }
    }
    fetchData()
  }, [])

  const handleLogout = async () => {
    try {
      await axios.post('http://localhost:8000/logout', {}, { withCredentials: true })
      // После логаута можно редиректить на страницу логина
      window.location.href = '/login'
    } catch (err) {
      console.error('Ошибка при выходе:', err)
    }
  }

  return (
    <div className="min-h-screen w-full bg-gray-50 text-gray-900 font-sans">
      <header className="w-full bg-white shadow p-6 flex justify-between items-center">
        <h1 className="text-3xl font-bold text-blue-700">Профиль</h1>
        <div className="text-right flex flex-col items-end gap-2">
          {user && (
            <>
              <div className="font-semibold text-lg">Баланс: ${user.balance}</div>
              <div className="text-sm text-gray-600">Тел: {user.phone_number}</div>
            </>
          )}
          <button
            onClick={handleLogout}
            className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Выйти
          </button>
        </div>
      </header>

      <main className="w-full p-6 flex flex-col items-center">
        {user && (
          <section className="w-full max-w-4xl bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-xl font-bold mb-4 text-blue-700">Данные пользователя</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p><span className="font-semibold">ID:</span> {user.id}</p>
                <p><span className="font-semibold">Страна:</span> {user.country}</p>
                <p><span className="font-semibold">IP:</span> {user.ip}</p>
              </div>
              <div>
                <p className="font-semibold mb-1">Устройства:</p>
                <ul className="list-disc pl-5">
                  {user.devices.map(device => (
                    <li key={device.device_id}>
                      {device.device} ({device.screen_width}x{device.screen_height})
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </section>
        )}

        <section className="w-full max-w-4xl bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4 text-blue-700">История переводов</h2>
          <div className="space-y-3">
            {transactions.map(tx => {
              const isSuccess = tx.status === 'success' && !tx.is_fraud
              const isBlocked = tx.status === 'blocked' || tx.is_fraud
              const bgColor = isSuccess
                ? 'bg-green-100 text-green-800'
                : 'bg-red-100 text-red-800'

              let actionText = ''
              if (isBlocked) {
                actionText = 'Заблокировано'
              } else {
                actionText = tx.direction === 'sent' ? 'Отправлено' : 'Получено'
              }

              return (
                <div
                  key={tx.id}
                  className={`p-4 rounded shadow flex justify-between items-center ${bgColor}`}
                >
                  <div>
                    <p><span className="font-semibold">ID:</span> {tx.id}</p>
                    <p><span className="font-semibold">Сумма:</span> ${tx.sum}</p>
                    <p><span className="font-semibold">Статус:</span> {tx.status}</p>
                    <p><span className="font-semibold">IP:</span> {tx.user_ip}</p>
                  </div>
                  <div className="font-bold text-lg">{actionText}</div>
                </div>
              )
            })}
          </div>
        </section>
      </main>
    </div>
  )
}
