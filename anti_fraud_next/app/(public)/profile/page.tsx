import Link from 'next/link'

export default function Profile() {
  const user = { name: 'Галымжан', phone: '+7700xxxxxxx', balance: 1200 }

  return (
    <div className="min-h-screen bg-gray-100 font-sans">
      <header className="flex justify-between items-center px-6 py-5 bg-white shadow">
        <h1 className="text-2xl font-bold">Профиль</h1>
        <Link href="/" className="text-blue-600 hover:underline">
          Главная
        </Link>
      </header>

      <main className="flex justify-center p-6">
        <div className="w-full max-w-md bg-white p-8 rounded-xl shadow-lg space-y-3">
          <h2 className="text-2xl font-bold text-gray-900">{user.name}</h2>
          <p className="text-gray-700">Телефон: {user.phone}</p>
          <p className="text-gray-900 font-semibold">Баланс: ${user.balance}</p>
        </div>
      </main>
    </div>
  )
}
