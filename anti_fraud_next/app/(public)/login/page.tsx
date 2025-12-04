'use client'

import { useState } from 'react'
import Link from 'next/link'
import { PAGES } from '@/app/config/pages.config'
import axios from 'axios'

export default function Login() {
  const [phone, setPhone] = useState('8')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handlePhoneChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let value = e.target.value.replace(/\D/g, '')
    if (!value.startsWith('8')) value = '8'
    if (value.length > 11) return
    setPhone(value)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    if (phone.length !== 11) {
      setError('Введите корректный номер')
      return
    }

    if (password.length < 4) {
      setError('Пароль минимум 4 символа')
      return
    }

    try {
      setLoading(true)
      const device = navigator.userAgent.slice(0, 65)

      const response = await axios.post(
        "http://localhost:8000/login",
        {
          phone_number: Number(phone),
          password: password,
          device: device,
          screen_width: window.screen.width,
          screen_height: window.screen.height
        },
        {
          withCredentials: true
        }
      )

      console.log('Успех:', response.data)
      // После успешного логина редирект на главную
      window.location.href = '/'  

    } catch (err: any) {
      console.error(err)
      setError(
        err?.response?.data?.detail || 'Ошибка входа. Проверьте номер или пароль.'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-100 font-sans">
      <div className="w-full max-w-[400px] rounded-xl bg-white p-8 shadow-lg">
        <h1 className="mb-6 text-center text-2xl font-bold text-gray-900">
          Вход
        </h1>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <input
            type="tel"
            value={phone}
            onChange={handlePhoneChange}
            placeholder="8XXXXXXXXXX"
            inputMode="numeric"
            className="rounded-md border border-gray-300 p-2 text-base text-gray-900 outline-none transition focus:border-blue-600 focus:ring-2 focus:ring-blue-200"
          />

          <input
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            placeholder="Пароль"
            className="rounded-md border border-gray-300 p-2 text-base text-gray-900 outline-none transition focus:border-blue-600 focus:ring-2 focus:ring-blue-200"
          />

          {error && (
            <div className="rounded-md bg-red-100 p-2 text-sm text-red-700">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="rounded-md bg-blue-700 py-2 text-base font-medium text-white transition hover:bg-blue-800 active:scale-[0.98] disabled:opacity-50"
          >
            {loading ? 'Загрузка...' : 'Войти'}
          </button>
        </form>

        <p className="mt-4 text-center text-gray-700">
          Нет аккаунта?{' '}
          <Link href={PAGES.Register()} className="text-blue-700 hover:underline">
            Регистрация
          </Link>
        </p>
      </div>
    </div>
  )
}
