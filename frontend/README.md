# frontend

## Project setup

```
npm install
```

The app reads the API endpoint from the `VUE_APP_API_URL` environment variable.
If unset it defaults to `/api/` which works with the built in dev proxy.

### Compiles and hot-reloads for development

```
npm run serve
```

The development script assigns `VUE_APP_API_URL` to
`http://127.0.0.1:8000/api/`.

### Compiles and minifies for production

```
npm run build
```

### Lints and fixes files

```
npm run lint
```

### Customize configuration

See [Configuration Reference](https://cli.vuejs.org/config/).
