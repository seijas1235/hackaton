# Frontend - Angular Standalone Application

Esta aplicación Angular standalone incluye integración con Angular Material, autenticación con AWS Cognito Hosted UI, y manejo de agentes AI con acciones configurables.

## 🚀 Características

- **Angular 20** con arquitectura standalone
- **Angular Material** con tema Azure/Blue
- **Autenticación AWS Cognito** con Hosted UI
- **Interceptores HTTP** para manejo automático de tokens
- **Guards de ruta** para protección de páginas
- **Servicios centralizados** para API y autenticación
- **Responsive design** con Material Design

## 📁 Estructura del Proyecto

```
src/
├── app/
│   ├── core/                     # Servicios centrales
│   │   ├── auth.service.ts       # Servicio de autenticación
│   │   ├── token.interceptor.ts  # Interceptor para tokens JWT
│   │   ├── auth.guard.ts         # Guards de protección de rutas
│   │   └── agent-api.service.ts  # Servicio para API de agentes
│   ├── dashboard/                # Componente Dashboard
│   ├── agent/                    # Componente Agentes
│   ├── actions/                  # Componente Acciones
│   ├── app.routes.ts            # Configuración de rutas
│   ├── app.config.ts            # Configuración de la aplicación
│   └── app.ts                   # Componente principal
├── environments/                 # Variables de entorno
└── styles.scss                 # Estilos globales
```

## ⚙️ Configuración de Environment

### Desarrollo (`src/environments/environment.ts`)

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:3000/api',
  cognitoDomain: 'your-cognito-domain.auth.region.amazoncognito.com',
  cognitoClientId: 'your-client-id',
  cognitoRedirectUri: 'http://localhost:4200/callback'
};
```

### Producción (`src/environments/environment.prod.ts`)

```typescript
export const environment = {
  production: true,
  apiUrl: 'https://your-api-domain.com/api',
  cognitoDomain: 'your-cognito-domain.auth.region.amazoncognito.com',
  cognitoClientId: 'your-client-id',
  cognitoRedirectUri: 'https://your-domain.com/callback'
};
```

### Variables de Environment Requeridas

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `apiUrl` | URL base de tu API backend | `https://api.example.com/api` |
| `cognitoDomain` | Dominio de Cognito Hosted UI | `example.auth.us-east-1.amazoncognito.com` |
| `cognitoClientId` | ID del cliente de Cognito | `1example23456789` |
| `cognitoRedirectUri` | URI de redirección post-login | `https://example.com/callback` |

## 🔧 Instalación y Desarrollo

### Prerrequisitos

- Node.js 18+ 
- npm 9+
- Angular CLI 20+

### Instalación

```bash
# Instalar dependencias
npm install

# Desarrollo local
ng serve

# Build para producción
ng build --prod
```

### Scripts Disponibles

```bash
# Desarrollo
npm start
ng serve

# Build
npm run build
ng build

# Tests
npm test
ng test

# Linting
npm run lint
ng lint

# Preview de producción
npm run preview
```

## 🔐 Configuración de AWS Cognito

### 1. Crear User Pool

```bash
# Via AWS CLI
aws cognito-idp create-user-pool \
  --pool-name "hackathon-users" \
  --policies '{"PasswordPolicy":{"MinimumLength":8,"RequireUppercase":true,"RequireLowercase":true,"RequireNumbers":true,"RequireSymbols":false}}' \
  --auto-verified-attributes email \
  --username-attributes email
```

### 2. Configurar App Client

```bash
# Crear app client
aws cognito-idp create-user-pool-client \
  --user-pool-id us-east-1_XXXXXXXXX \
  --client-name "hackathon-web-client" \
  --generate-secret false \
  --supported-identity-providers COGNITO \
  --callback-urls "http://localhost:4200/callback,https://your-domain.com/callback" \
  --logout-urls "http://localhost:4200,https://your-domain.com" \
  --allowed-o-auth-flows code \
  --allowed-o-auth-scopes openid,email,profile \
  --allowed-o-auth-flows-user-pool-client
```

### 3. Configurar Hosted UI Domain

```bash
# Crear dominio personalizado
aws cognito-idp create-user-pool-domain \
  --domain "your-cognito-domain" \
  --user-pool-id us-east-1_XXXXXXXXX
```

### 4. Configuración del Environment

Actualizar `src/environments/environment.ts` con los valores de Cognito:

```typescript
export const environment = {
  // ... otras configuraciones
  cognitoDomain: 'your-cognito-domain.auth.us-east-1.amazoncognito.com',
  cognitoClientId: 'your-app-client-id',
  cognitoRedirectUri: 'http://localhost:4200/callback'
};
```

## 🚀 Deploy en AWS Amplify

### Opción 1: Deploy Manual

```bash
# Build de producción
ng build --prod

# Comprimir archivos
cd dist/frontend-app
zip -r ../frontend-app.zip .

# Subir a Amplify via Console
```

### Opción 2: Deploy con Amplify CLI

```bash
# Instalar Amplify CLI
npm install -g @aws-amplify/cli

# Configurar Amplify
amplify configure

# Inicializar proyecto
amplify init

# Agregar hosting
amplify add hosting

# Deploy
amplify publish
```

### Opción 3: Configuración Manual en Amplify Console

1. **Crear Nueva App en Amplify Console**
   - Ir a AWS Amplify Console
   - Seleccionar "Deploy without Git provider"
   - Subir archivo ZIP del build

2. **Configurar Build Settings**

Crear `amplify.yml` en el root del proyecto:

```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - npm ci
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: dist/frontend-app
    files:
      - '**/*'
  cache:
    paths:
      - node_modules/**/*
```

3. **Variables de Environment en Amplify**

En Amplify Console > App Settings > Environment Variables:

| Clave | Valor |
|-------|-------|
| `API_URL` | `https://your-api-domain.com/api` |
| `COGNITO_DOMAIN` | `your-cognito-domain.auth.region.amazoncognito.com` |
| `COGNITO_CLIENT_ID` | `your-client-id` |

4. **Configurar Redirects/Rewrites**

En Amplify Console > App Settings > Rewrites and redirects:

```
Source: </^[^.]+$|\.(?!(css|gif|ico|jpg|js|png|txt|svg|woff|ttf|map|json)$)([^.]+$)/>
Target: /index.html
Type: 200 (Rewrite)
```

### Opción 4: Deploy con GitHub Actions

Crear `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Amplify

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Build
      run: npm run build
      env:
        API_URL: ${{ secrets.API_URL }}
        COGNITO_DOMAIN: ${{ secrets.COGNITO_DOMAIN }}
        COGNITO_CLIENT_ID: ${{ secrets.COGNITO_CLIENT_ID }}
    
    - name: Deploy to Amplify
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1
    
    - name: Upload to Amplify
      run: |
        aws amplify start-deployment \
          --app-id ${{ secrets.AMPLIFY_APP_ID }} \
          --branch-name main \
          --source-url s3://your-deployment-bucket/frontend-app.zip
```

## 🔨 Configuración Avanzada

### Custom Domain

```bash
# Via AWS CLI
aws amplify create-domain-association \
  --app-id d1example2345 \
  --domain-name example.com \
  --sub-domain-settings "prefix=www,branchName=main"
```

### SSL Certificate

Amplify automáticamente provisiona certificados SSL via AWS Certificate Manager.

### Performance Optimization

En `angular.json`, configurar optimizaciones:

```json
{
  "projects": {
    "frontend-app": {
      "architect": {
        "build": {
          "configurations": {
            "production": {
              "optimization": true,
              "outputHashing": "all",
              "sourceMap": false,
              "namedChunks": false,
              "extractLicenses": true,
              "vendorChunk": false,
              "buildOptimizer": true,
              "budgets": [
                {
                  "type": "initial",
                  "maximumWarning": "500kb",
                  "maximumError": "1mb"
                }
              ]
            }
          }
        }
      }
    }
  }
}
```

## 🏗️ Arquitectura y Servicios

### AuthService

Maneja toda la lógica de autenticación con Cognito:

- Login con Hosted UI
- Manejo de tokens JWT
- Refresh automático de tokens
- Logout y limpieza de sesión

### TokenInterceptor

Intercepta todas las peticiones HTTP para:

- Agregar automáticamente el token Bearer
- Manejar errores 401 y refresh de tokens
- Excluir endpoints de autenticación

### AgentApiService

Servicio centralizado para todas las operaciones de API:

- Gestión de agentes
- Sesiones de chat
- Ejecución de acciones
- Métricas de dashboard

### AuthGuard

Protege rutas que requieren autenticación:

- Verifica estado de autenticación
- Redirige a login si no está autenticado
- Guarda URL de destino para redirección post-login

## 🎨 Personalización de UI

### Temas de Angular Material

El tema actual es Azure/Blue. Para cambiar:

```typescript
// En app.config.ts
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';

// Para tema personalizado, editar styles.scss
@use '@angular/material' as mat;

$custom-primary: mat.define-palette(mat.$indigo-palette);
$custom-accent: mat.define-palette(mat.$pink-palette, A200, A100, A400);
$custom-theme: mat.define-light-theme((
  color: (
    primary: $custom-primary,
    accent: $custom-accent,
  )
));

@include mat.all-component-themes($custom-theme);
```

## 🔍 Debugging y Troubleshooting

### Problemas Comunes

1. **Error de CORS**
   ```
   Solución: Configurar CORS en el backend para permitir el origen de Amplify
   ```

2. **Token Expirado**
   ```
   Verificar: El TokenInterceptor debería manejar esto automáticamente
   ```

3. **Redirección de Cognito Fallida**
   ```
   Verificar: URLs de callback en la configuración de Cognito
   ```

### Logs y Monitoreo

```typescript
// Habilitar logs detallados en development
if (!environment.production) {
  console.log('API URL:', environment.apiUrl);
  console.log('Cognito Domain:', environment.cognitoDomain);
}
```

## 📈 Monitoreo en Producción

### CloudWatch Integration

Amplify automáticamente envía logs a CloudWatch. Para métricas personalizadas:

```typescript
// En agent-api.service.ts
private logMetric(action: string, duration: number) {
  if (environment.production) {
    // Enviar métricas a CloudWatch
    console.log(`Metric: ${action} took ${duration}ms`);
  }
}
```

### Error Tracking

Para tracking de errores, integrar con services como:

- AWS X-Ray
- Sentry
- Rollbar

## 🔧 Comandos Útiles

```bash
# Verificar configuración de Amplify
amplify status

# Ver logs de build
amplify console

# Actualizar backend
amplify push

# Eliminar recursos
amplify delete
```

## 📚 Recursos Adicionales

- [Angular Documentation](https://angular.dev)
- [Angular Material](https://material.angular.io)
- [AWS Amplify Documentation](https://docs.amplify.aws)
- [AWS Cognito Developer Guide](https://docs.aws.amazon.com/cognito)

## 🤝 Contribución

1. Fork el proyecto
2. Crear feature branch (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push al branch (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.