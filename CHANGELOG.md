# 변경 이력

## 0.1.0 (2025-05-24)

최초 프리릴리즈.

### 폰트
- Inter Variable (opsz + wght)과 Pretendard JP Variable (wght) 합침
- CJK 수직 정렬: Y offset +21 (Pretendard의 가-H center diff와 동일)
- CJK 회색도 매칭: 수평 1% 축소로 라틴과 시각적 굵기 균형
- CJK 광학 크기: opsz=32(Display)에서 3% 축소
- ₩ (원화 기호)를 Pretendard JP의 한국식 글리프로 교체
- `rclt` 피처: CJK 인접 시 49개 기호가 자동으로 .case 버전으로 치환
- Vertical Metrics: ratio 1.125, cap center 기준 대칭 (asc=1897, desc=-407)
- 피그마에서 12/14/16/18px Line Height 짝수

### OpenType
- Inter의 모든 피처 유지 (calt, ccmp, case, dlig, frac, tnum, zero, cv01-16, ss01-08)
- `rclt` 추가: CJK 컨텍스트 기호 정렬
- GSUB/GPOS에 CJK 스크립트 등록 (hang, kana, hani)

### 배포
- Variable TTF: InterCJKVariable.ttf, InterCJKDisplayVariable.ttf
- Static TTF/OTF: 9 weight × 2 패밀리 = 36 파일
- 웹: woff2 (variable + static) + dynamic subset (119분할 × 2)
- CSS: local() 폴백 + @font-feature-values + 개별 weight CSS + minified
- npm: `inter-cjk` 패키지, jsDelivr CDN 지원

### 빌드
- 소스: Inter (git submodule) + Pretendard JP (릴리즈 다운로드)
- 파이프라인: fontmake → merge (build-full.py) → split-opsz → gen-static → woff2 → dynamic-subset
- 재현 가능: `make all`로 클린 빌드
