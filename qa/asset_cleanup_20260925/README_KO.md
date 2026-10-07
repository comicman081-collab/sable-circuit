# 2026-09-25 이전 사이트 배포 압축본 폐기

사용자 요청에 따라 이전 사이트 배포용 압축본 7개를 `_retired_20260924/_DELETE_ONLY_OLD_SITE_PACKAGES_20260925/`에 따로 모았다. 이 전용 폴더 안에는 아래 7개 파일만 있다. 파일별 크기와 SHA-256은 `qa/asset_cleanup_20260924/retirement_manifest.jsonl`의 동일한 원래 경로 기록과 일치함을 확인했다. 영구 삭제 명령은 실행 정책에 의해 거부되어 파일은 사용자가 직접 삭제할 수 있도록 격리 상태로 남겼다.

| 원래 경로 | 바이트 |
|---|---:|
| `qa/demo_web_20260920/site.tar.gz` | 233410367 |
| `qa/continuous_map_20260923/site_publish.tar.gz` | 233158967 |
| `qa/site_publish_20260923/sable_site_v7.tar.gz` | 233156403 |
| `qa/site_publish_20260923/sable_site_v8.tar.gz` | 212076303 |
| `qa/site_publish_20260923/sable_site_v9.tar.gz` | 212074913 |
| `qa/site_publish_20260923/sable_site_v10.tar.gz` | 212073905 |
| `qa/site_publish_20260923/sable_site_v11.tar.gz` | 212073658 |

합계 1,548,024,516바이트(약 1.44GiB). `web_demo/dist`의 현재 사이트 실행 묶음, `web_demo/.git`, 사운드·인트로 자료 및 공개 사이트 배포 상태는 삭제 대상에서 제외했다. 전용 폴더를 삭제하면 이 7개 압축본만 제거된다. `_retired_20260924/` 상위 폴더 전체를 삭제하면 다른 격리 자산까지 함께 제거되므로, 이번 범위에서는 상위 폴더를 삭제하지 않는다. SSD 공간은 아직 회수되지 않았다.
