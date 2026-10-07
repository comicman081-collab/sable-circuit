| 갈래 | 판 수 | 추출 | 전멸·기타 | 걸린 시간(s) | 받은 피해(HP) | 마지막 방 깊이 |
|---|---:|---:|---:|---|---|---|
| 중립 계약(러너의 `full_op_01`과 같은 호출) | 3 | **3** | 0 | 135.6 / 123.0 / 122.3 | 415.6 / 287.0 / 352.0 | 6 / 6 / 6 |
| 실제 run id의 기본 제안(`build`) | 3 | **3** | 0 | 129.2 / 118.5 / 127.3 | 403.3 / 389.6 / 360.3 | 6 / 6 / 6 |
| REDLINE | 3 | **0** | 3 | 117.5 / 112.3 / 107.6 | 450.3 / 439.1 / 427.9 | 4 / 4 / 4 |

판별 상세:

| 라운드 | 갈래 | 계약 | 결과 | 시간(s) | 피해 | 깊이 | 실패한 검사 |
|---:|---|---|---|---:|---:|---:|---|
| 0 | neutral | `neutral` | EXTRACTED | 135.6 | 415.6 | 6 | - |
| 0 | default | `default:CH01-RUN-000011` | EXTRACTED | 129.2 | 403.3 | 6 | - |
| 0 | redline | `redline` | WIPED | 117.5 | 450.3 | 4 | Live combat and extraction succeed without cheats; All six rooms reached; not early extraction; All authored waves and boss defeated through real damage |
| 1 | neutral | `neutral` | EXTRACTED | 123.0 | 287.0 | 6 | - |
| 1 | default | `default:CH01-RUN-000018` | EXTRACTED | 118.5 | 389.6 | 6 | - |
| 1 | redline | `redline` | WIPED | 112.3 | 439.1 | 4 | Live combat and extraction succeed without cheats; All six rooms reached; not early extraction; All authored waves and boss defeated through real damage |
| 2 | neutral | `neutral` | EXTRACTED | 122.3 | 352.0 | 6 | - |
| 2 | default | `default:CH01-RUN-000025` | EXTRACTED | 127.3 | 360.3 | 6 | - |
| 2 | redline | `redline` | WIPED | 107.6 | 427.9 | 4 | Live combat and extraction succeed without cheats; All six rooms reached; not early extraction; All authored waves and boss defeated through real damage |
