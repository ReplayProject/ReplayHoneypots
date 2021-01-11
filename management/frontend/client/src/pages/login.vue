<template>
    <main
        class="w-100 ph3-m ph3-l"
        :class="{
            'w-75-m': $route.name != 'overview',
            'w-75-l': $route.name != 'overview',
        }"
    >
        <component-title>
            <template v-slot:pageCategory>Welcome</template>
            <template v-slot:pageName>Login</template>
        </component-title>
        <hr class="o-20" />
        <main class="black-80">
            <form class="measure" @submit="login" autocomplete="off" ref="form">
                <fieldset id="sign_up" class="ba b--transparent ph0 mh0">
                    <div class="mt3">
                        <label class="db fw6 lh-copy f6" for="username">Username</label>
                        <input
                            class="pa2 input-reset ba bg-transparent hover-bg-black hover-white w-100"
                            type="username"
                            v-model="username"
                            name="username"
                            id="username"
                        />
                    </div>
                    <div class="mv3">
                        <label class="db fw6 lh-copy f6" for="password">Password</label>
                        <input
                            class="b pa2 input-reset ba bg-transparent hover-bg-black hover-white w-100"
                            type="password"
                            v-model="password"
                            name="password"
                            id="password"
                        />
                    </div>
                </fieldset>
                <div class="">
                    <input
                        class="b ph3 pv2 input-reset ba b--black bg-transparent grow pointer f6 dib"
                        type="submit"
                        name="btnSignIn"
                        value="Sign in"
                    />
                    <input
                        class="b ph3 pv2 input-reset ba b--black bg-transparent grow pointer f6 dib"
                        type="button"
                        value="SSO Portal"
                        onclick="window.location.href='/login/sso';"
                    />
                </div>

                <section class="ph2 pt2">
                    <p class="ma3 pa2 i tc w-100">
                        If you get redirected here after a SAML SSO login, your SSO
                        account does not have access to this application, or your local
                        account is disabled. Contact your IT department.
                    </p>
                </section>
                <!-- <div class="lh-copy mt3">
          <a href="#0" class="f6 link dim black db">Sign up</a>
          <a href="#0" class="f6 link dim black db">Forgot your password?</a>
        </div> -->
            </form>
        </main>
    </main>
</template>

<script>
import componentTitle from '../components/title'

export default {
    name: 'Login',
    components: {
        componentTitle,
    },
    data() {
        return {
            username: '',
            password: '',
        }
    },
    methods: {
        /**
         * Attempt user login
         */
        async login(e) {
            e.preventDefault()

            let data = {
                username: this.username,
                password: this.password,
            }

            try {
                let res = await this.axios.post('/login', data)
                this.$toasted.show('Authenticated')
                this.$router.push('/dashboard')
                this.$root.$emit('login')
            } catch (error) {
                this.$toasted.show('Failed to Login. Error: ' + error.message)
                if (process.env.NODE_ENV != 'test') console.log('Cannot log in', error)
            }
        },
    },
}
</script>
