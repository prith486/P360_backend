# Environment Security Checklist

## ✅ Pre-Commit Checklist
- [ ] `.env` file is in `.gitignore`
- [ ] No API keys in `.env.example`
- [ ] No hardcoded secrets in source code
- [ ] `SECRET_KEY` is 32+ characters random string

## ✅ Production Checklist
- [ ] `DEBUG=False`
- [ ] `ENVIRONMENT=production`
- [ ] `ALLOWED_ORIGINS` strictly defined
- [ ] Swagger docs disabled
- [ ] SSL enabled for DB and Redis

## 🚫 Never Commit
- `.env` file
- `secrets/` folders
- Log files
