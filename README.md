# Compliance Fort

**Batch ZK-proof verification via Fortran FFI**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Fortran](https://img.shields.io/badge/Fortran-90%2F95-green.svg)](https://gcc.gnu.org/fortran/)

## Идея

Массовая верификация Zero-Knowledge доказательств для compliance-аудита.

**Почему Fortran?**
- Один вызов FFI для 10000 proofs вместо 10000 вызовов
- Fortran оптимизирован для числовых массивов
- Возможность OpenMP параллелизации

**Когда это имеет смысл:**
- Аудит-система получает пачку транзакций с ZK-доказательствами
- Нужно быстро проверить все доказательства
- Количество: 1000+ proofs за запрос

**Когда НЕ имеет смысл:**
- Единичные операции (Python справится за ~1мс)
- Нужна production криптография (используй libsecp256k1)

## Quick Start

```bash
# Docker
docker-compose up --build

# Local
make lib && make api && make run
```

API: http://localhost:8000/docs

## API Endpoints

### Batch Verify (главный)

```bash
curl -X POST "http://localhost:8000/api/v1/batch/verify" \
  -H "Content-Type: application/json" \
  -d '{
    "public_key": 17,
    "proofs": [
      {"id": 1, "data": 10, "proof_r": 10, "proof_s": 15, "public_key": 17},
      {"id": 2, "data": 20, "proof_r": 8, "proof_s": 12, "public_key": 17}
    ]
  }'
```

Response:
```json
{
  "total": 2,
  "valid_count": 2,
  "invalid_count": 0,
  "results": [true, true],
  "elapsed_ms": 0.15
}
```

### Batch Create

```bash
curl -X POST "http://localhost:8000/api/v1/batch/create" \
  -H "Content-Type: application/json" \
  -d '{
    "secret_key": 7,
    "items": [
      {"id": 1, "data": 100},
      {"id": 2, "data": 200}
    ]
  }'
```

### Single Operations

- `POST /api/v1/proof/create` - создать один proof
- `POST /api/v1/proof/verify` - проверить один proof
- `POST /api/v1/key/generate` - сгенерировать public key

## Architecture

```
┌─────────────────┐
│   FastAPI       │  REST API
│   (Python)      │
└────────┬────────┘
         │ ctypes FFI (batch calls)
         ▼
┌─────────────────┐
│  Fortran Core   │  batch_verify, batch_create
│  Schnorr ZK     │  mod_pow, verify_proof
└─────────────────┘
```

## Ограничения

**Это демо-проект:**
- PRIME=23 (нужно 256+ бит для безопасности)
- Нет криптографического RNG
- Schnorr упрощён для наглядности

**Для продакшена нужно:**
- Использовать большие простые числа (2048+ бит)
- Заменить на cryptographically secure RNG
- Провести security audit
- Рассмотреть libsodium/libsecp256k1

## Development

```bash
make lib      # Скомпилировать Fortran
make api      # Установить Python deps
make test     # Запустить тесты
make clean    # Очистить артефакты
```

## License

MIT
