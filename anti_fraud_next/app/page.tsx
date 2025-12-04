'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import axios from 'axios'

export default function Home() {
  const [balance, setBalance] = useState<number | null>(null)
  const [receiver, setReceiver] = useState('8')
  const [amount, setAmount] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  // Получаем данные пользователя
  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await axios.get('http://localhost:8000/me', {
          withCredentials: true, // важно для cookie
        })
        setBalance(response.data.balance)
      } catch (err) {
        console.error(err)
      }
    }
    fetchUser()
  }, [])

  const handlePhoneChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let value = e.target.value.replace(/\D/g, '')
    if (!value.startsWith('8')) value = '8'
    if (value.length > 11) return
    setReceiver(value)
  }

  const handleAmountChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.replace(/\D/g, '')
    setAmount(value)
  }

  const handleTransfer = async () => {
    setError(null)
    setSuccess(null)

    if (receiver.length !== 11) {
      setError('Введите корректный номер получателя')
      return
    }
    if (!amount || Number(amount) <= 0) {
      setError('Введите корректную сумму')
      return
    }

    try {
      setLoading(true)
      const response = await axios.post(
        'http://localhost:8000/transaction',
        {
          receiver,
          sum: Number(amount),
        },
        { withCredentials: true }
      )
      setSuccess('Перевод выполнен успешно!')
      setReceiver('8')
      setAmount('')
      setBalance(prev => (prev !== null ? prev - Number(amount) : null))
    } catch (err: any) {
      console.error(err)
      setError(err?.response?.data?.detail || 'Ошибка перевода')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-100 font-sans text-gray-900">
      <header className="flex justify-between items-center px-6 py-5 bg-white shadow">
        <h1 className="text-2xl font-bold">Главная</h1>
        <div className="flex items-center gap-4">
          <span className="font-semibold">Баланс: ${balance ?? '...'}</span>
          <Link href="/profile">
            <button className="px-4 py-2 bg-blue-700 text-white rounded-md hover:bg-blue-800">
              Профиль
            </button>
          </Link>
        </div>
      </header>

      <main className="p-6 max-w-md mx-auto">
        <h2 className="text-xl font-bold mb-4">Сделать перевод</h2>
        {error && <div className="mb-2 p-2 bg-red-100 text-red-700 rounded">{error}</div>}
        {success && <div className="mb-2 p-2 bg-green-100 text-green-700 rounded">{success}</div>}

        <input
          type="tel"
          value={receiver}
          onChange={handlePhoneChange}
          placeholder="Номер получателя 8XXXXXXXXXX"
          className="w-full mb-3 p-2 border border-gray-400 rounded outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-200"
        />
        <input
          type="text"
          value={amount}
          onChange={handleAmountChange}
          placeholder="Сумма перевода"
          className="w-full mb-3 p-2 border border-gray-400 rounded outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-200"
        />

        <button
          onClick={handleTransfer}
          disabled={loading}
          className="w-full py-2 bg-blue-700 text-white rounded hover:bg-blue-800 disabled:opacity-50"
        >
          {loading ? 'Перевод...' : 'Отправить'}
        </button>
      </main>
    </div>
  )
}
