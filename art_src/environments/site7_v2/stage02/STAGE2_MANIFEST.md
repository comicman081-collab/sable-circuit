# SITE-7 v2 단계 2 원화 매니페스트

작전 `MIS_CH01_02` 전용 방 8장·통로 7장. 내장 ImageGen으로 각 판을 순차 생성하고 시각 확인한 1회차 원본을 선택했다. 경로 오류로 생성이 시작되지 않은 호출은 시도로 세지 않았다. 승인된 단계 1 판은 기하·조명 기준, 이전 v1 판은 구역 정체성 참고에만 사용했다.

모든 RAW와 MASTER는 선택 후보 및 Codex 관리 스테이징 이미지와 SHA-256이 같다. GAME은 네이티브 크기 RGB를 유지하며 명시된 판 전체 sRGB 노출 계수만 한 번 적용했다. 크롭·리사이즈·반전·회전·부분 칠은 없다. 자세한 프롬프트 전문, 참조 이미지 경로/해시와 관리 스테이징 경로/해시는 [생성 로그](stage2_generation_log.json), 실제 픽셀 바닥/문 윤곽은 [기하 기록](geometry_stage2.json), 파생 해시는 [파생 기록](stage2_derivatives.json)에 있다.

| 판 | 크기 | RAW / MASTER SHA-256 | GAME SHA-256 | sRGB 계수 | 문 / 데크 |
|---|---:|---|---|---:|---|
| S2_R01 | 1672×941 | `10be6a74135ef21e515dfe1493329cbe0c6540279e262a52b19250ecd4869279` | `39d4868c6d05da8a6a28bbf7ac872288e48f8d6171f7940f3dce28a517dfe0a3` | 0.724 | NE |
| S2_R02 | 1774×887 | `cafeab770a8b21f4aa606beb1c369ecb4eadd9449b3c14b595361f1c0b54197b` | `a00077d3e4fbf2ea42393e366730ec1b1be079729bcc876783cc9b2bd6b46bb0` | 0.800 | SW, NE |
| S2_R03 | 1672×941 | `4e04229338f65207e78355157f48f7811b7a11c01116e55b03d323d06b69aa79` | `b5750dc9a2a629fd02572e9f82ad372817eca783429dd2490b2c865532fd70b0` | 0.667 | SW, NE, SE |
| S2_R04 | 1672×941 | `7d15d22a6d734813f69fca8f398980650dc08a80f741220f709fed02bd3478fb` | `50cf7902c5f45eff5cab0a1dbcc25dc65352cce08fb7c6a6feb62358facf687a` | 0.718 | SW, NE, SE |
| S2_R05 | 1672×941 | `ef69ee88e99612c4c8eb7a5de8da79ea6e580168758a24854d32267c2f264017` | `d47b73d29b2d6abd03e0df7b1ed72fa178302f5cb19cf8cc5c206aa250d6b8ce` | 0.620 | SW, NE |
| S2_R06 | 1672×941 | `326c27a2df43f3fa82fa2a5ca4e5a291c778d9a51f0c6b768e5e04c0e836ea72` | `91bc6a826e3cfa69a2737f45698d4f73b930fd392bb3a42d9009c8bb714164af` | 0.698 | SW |
| S2_O01 | 1774×887 | `bdab47240260ba36ab304d5b853cbb76c6cee3957f576ff83fedb72fc3ee02cb` | `95afe2c316a572cfb07316a1455068e7ea8b7b2956dcc7f8ce1ed4d0d8e1c877` | 0.609 | NW |
| S2_O02 | 1774×887 | `f4e986cd582f87863156e1a0bc6254c7b01161d40d44193cfd2d7acc0fd3f560` | `d484a0602a5e2620ca0f6f2a6ef14b77612a4369bff35262f2f01f86c34608ea` | 0.639 | NW |
| S2_C01 | 1402×1122 | `c61fa1b2fcc9c706be5983c702a3f3db294e6a0e6cdb67faf5decc9a52af6495` | `38077524519c161a75e34841656b7f056a2c1c2e32e9657af2823dd56d4c9ca5` | 0.811 | ascending |
| S2_C02 | 1402×1122 | `18e22ce696d5385c236fdb3c414c263109b7da7d958e80ebcbd94bded27a36b7` | `dcb6f2d070143618747803cf137101d25f793fb8dafd68f4912361bce06868e6` | 0.737 | ascending |
| S2_C03 | 1402×1122 | `45b01e833be1a4da7457ee41da4189ac02b5927061df575474ffd1f07ab8c1a2` | `ca1842adbe92b199fc47b360a9756df50b196d7e83c0bf721b15baa63fc01499` | 0.744 | ascending |
| S2_C04 | 1402×1122 | `cfbd3c6d9047322bae3816f75571249fc1c2efaa04da4e9a57119ba6ffe0c66e` | `f6a2590a1949c893cdcfc81ff128fc5278ae4edec420f594f29d27268a23bce9` | 0.711 | ascending |
| S2_C05 | 1402×1122 | `166cdef25d582ba39a9663312e340af87f721973d44249877d2c077568c855aa` | `83d9217f15eda6028387ae50d85848c7bb1398415f4341dfee55f428b9486828` | 0.657 | ascending |
| S2_C06 | 1254×1254 | `87c7f9163ccaf3f1ceaa555da98d5ec29950cbcd00a4c3bb0849601c7474be62` | `133068b5698e2904f8b03daaac1408fd527a91075d7f3f96c15ba141b9b41752` | 0.819 | descending |
| S2_C07 | 1254×1254 | `c01ed751e3d22d3fd03f0d5b8afde8042d01fdbce42162b55fb9ee54642d3d25` | `c66333f450e0360cff6e273ffef79ec7e43a41399a5526fd79333db4a45d7567` | 0.771 | descending |

작전 2 런타임 포인터와 바닥 기록만 교체했다. 런타임 배율은 1.0, 상승 통로 5장은 `ascending`, 비반전 하강 갈래 2장은 `descending`이다. 원본과 Codex 관리 스테이징 이미지는 작업 종료 전 삭제하지 않는다. 이 배치에서 거절된 생성 이미지는 없다. 이전 v1 원화도 삭제하지 않았다.

기술·게임 검증과 캡처는 `qa/site7_map_kit_v2_20260927_stage2/`에 기록한다. 작전 1, 3, 4, 5의 원화와 미션 데이터는 변경하지 않는다.
