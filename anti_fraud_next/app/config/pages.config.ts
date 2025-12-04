class PagesConfig {
    PROFILE(username: string) {
        return `profile/${username}`;
    }
    HOME() {
        return '/';
    }
    Login() {
        return '/login';
    }
    Register() {
        return '/register';
    }
}

export const PAGES = new PagesConfig();
