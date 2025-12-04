import { NextRequest, NextResponse } from 'next/server'

export function middleware(request: NextRequest) {
  const token = request.cookies.get('my_access_token')?.value

  const { pathname } = request.nextUrl

  const publicPaths = ['/login', '/register']


  if (!token && !publicPaths.some(path => pathname.startsWith(path))) {
    return NextResponse.redirect(new URL('/login', request.url))
  }


  if (token && publicPaths.some(path => pathname.startsWith(path))) {
    return NextResponse.redirect(new URL('/', request.url))
  }

  return NextResponse.next()
}


export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
}
