# 작업 시작·완료 Git 워크플로우 자동화 설계

- 상태: 사용자 검토 대기
- 작성일: 2026-09-17
- 대상 저장소: `team-ttobagi/seoul-data-analysis`

## 1. 목적

팀원이 반복적으로 수행하는 GitHub 이슈 생성, 기준 브랜치 동기화, 작업 브랜치 생성, 검사, 커밋, push, PR 생성을 일관된 로컬 명령으로 묶는다.

자동화는 로컬에서 실행한다. GitHub Actions는 이 기능의 실행 엔진으로 사용하지 않으며, 이후 별도 CI를 추가할 때만 push 또는 PR 검증에 사용한다.

## 2. 확정 요구사항

- 기본 기준 브랜치는 `dev`다.
- 작업 시작 명령은 대화형 입력과 명령어 인자를 모두 지원한다.
- 이슈는 기존 `.github/ISSUE_TEMPLATE/issue-template.md` 형식을 사용한다.
- 이슈 생성 후 이슈 번호를 포함한 브랜치를 만든다.
- 브랜치 형식은 `{issue-number}-{type}-{한글-slug}`다.
  - 예: `123-feat-로그인-페이지`
- 작업 트리가 깨끗하지 않으면 작업 시작을 중단한다.
- 자동 stash, 자동 삭제는 수행하지 않는다.
- 작업 완료 검사는 변경 경로에 따라 실행한다.
  - `frontend/` 변경: `npm run build`, `npm run lint`
  - `backend/` 변경: `uv run pytest` (작업 디렉터리 `backend`)
  - 양쪽 변경: 양쪽 검사 모두 실행
  - 문서만 변경: 코드 검사를 실행하지 않음
- 검사 실패 시 commit, push, PR을 진행하지 않는다.
- `--skip-check`를 사용한 경우에만 검사를 우회한다.
- 파일 선택과 staging은 기존 팀 방식대로 VS Code에서 직접 수행한다.
- commit 대상은 staged 파일뿐이다.
- PR에는 이슈 연결과 기존 PR 템플릿을 사용한다.
- 라벨과 리뷰어는 자동 지정하지 않는다.
- PR은 draft가 아닌 바로 리뷰 가능한 상태로 생성한다.
- 커밋 메시지 형식은 `[type] 요약 #issue-number`다.
  - 예: `[feat] 로그인 페이지 구현 #123`
- 별도 의존성 설치 없이 표준 Python으로 핵심 로직을 실행한다.
- macOS용 짧은 실행 래퍼를 제공하고, 다른 운영체제에서는 Python 진입점을 직접 실행할 수 있다.

## 3. 사용자 인터페이스

### 3.1 macOS 대화형 시작

```bash
./scripts/start-task
```

동작 순서:

1. `git`, `gh`, Python 및 저장소 상태를 확인한다.
2. 작업 트리가 깨끗하지 않으면 변경 파일을 표시하고 종료한다.
3. `dev`로 이동하고 `git pull --ff-only origin dev`를 실행한다.
4. 작업 타입과 제목을 입력받는다.
5. 기존 이슈 템플릿이 채워진 임시 파일을 기본 편집기로 연다.
6. 저장 후 GitHub 이슈를 생성한다.
7. 생성된 이슈 URL에서 번호를 얻는다.
8. 제목을 정규화해 한글 slug를 만들고 작업 브랜치를 생성·checkout한다.

이슈가 생성된 뒤 브랜치 생성이 실패하면 생성된 이슈 URL과 수동 복구 방법을 표시한다. 이미 생성된 이슈를 자동 삭제하지 않는다.

### 3.2 비대화형 시작

```bash
./scripts/start-task \
  --type feat \
  --title "로그인 페이지 구현" \
  --body-file ./issue-body.md
```

`--type`, `--title`, `--body-file`이 모두 있어야 비대화형으로 실행한다. `--body-file`이 없거나 읽을 수 없으면 이슈를 생성하지 않고 종료한다.

### 3.3 작업 완료 검사

```bash
./scripts/finish-task
```

첫 실행은 commit·push·PR을 수행하지 않고 다음만 수행한다.

1. 현재 브랜치가 작업 브랜치 형식인지 확인한다.
2. 변경 경로를 확인해 필요한 검사를 실행한다.
3. 검사 결과와 변경 파일을 표시한다.
4. staged 파일이 없거나 staging되지 않은 변경이 남아 있으면 VS Code에서 파일을 선택하라는 안내를 표시한다.
5. 검사 결과와 staging 상태를 표시한 뒤 `--continue` 실행을 안내하고 종료한다.

검사 실패 시 실패 명령과 출력을 표시하고 종료한다. `--skip-check`를 사용하면 검사를 생략하고 PR 본문에 생략 사실을 기록할 준비를 한다. `--skip-check`는 첫 검사와 `--continue` 양쪽에서 사용할 수 있다.

### 3.4 staged 파일 제출

팀원이 VS Code Source Control에서 원하는 파일을 직접 Stage한 후 다음을 실행한다.

```bash
./scripts/finish-task --continue
```

`--continue`는 제출 직전에 검사를 다시 실행한다. 첫 검사 이후 파일이 추가로 수정되었거나 검사 상태가 오래된 경우를 보호하기 위한 동작이다. `--skip-check`를 함께 사용하면 이 재검사를 생략한다.

검사를 통과한 뒤 `--continue`는 다음을 수행한다.

1. staged 파일이 하나 이상인지 확인한다.
2. `git diff --cached`를 표시한다.
3. unstaged 변경이 남아 있으면 staged 파일만 commit한다는 경고를 표시한다.
4. 커밋 메시지 요약을 입력받는다.
5. 최종 정보를 표시하고 commit·push·PR 생성 여부를 한 번 확인한다.
6. 승인 시 staged 파일만 commit한다.
7. 현재 브랜치를 `origin`에 push한다.
8. 기존 PR 템플릿을 바탕으로 PR을 생성한다.
9. PR 본문에 `Closes #<issue-number>`를 포함한다.

승인하지 않으면 staged 상태를 유지한 채 종료한다. push 성공 후 PR 생성이 실패하면 브랜치와 커밋을 보존하고 PR 재실행 명령을 표시한다.

## 4. 구성 요소

```text
scripts/taskflow.py          표준 Python 진입점과 명령 처리
scripts/start-task            macOS용 start 래퍼
scripts/finish-task           macOS용 finish 래퍼
scripts/taskflow.config.json  기준 브랜치·템플릿·검사 명령 설정
docs/CONTRIBUTING.md          팀원 설치 및 사용 안내
```

`taskflow.py`는 GitHub API를 직접 구현하지 않고 `git`과 `gh`를 subprocess로 호출한다. 이슈·PR·인증은 팀원의 기존 GitHub CLI 권한을 사용한다. 토큰을 파일에 저장하지 않는다.

설정 파일의 기본값은 다음과 같다.

```json
{
  "base_branch": "dev",
  "issue_template": ".github/ISSUE_TEMPLATE/issue-template.md",
  "pull_request_template": ".github/PULL_REQUEST_TEMPLATE.md",
  "checks": {
    "frontend": {
      "paths": ["frontend/"],
      "cwd": "frontend",
      "commands": [["npm", "run", "build"], ["npm", "run", "lint"]]
    },
    "backend": {
      "paths": ["backend/"],
      "cwd": "backend",
      "commands": [["uv", "run", "pytest"]]
    }
  }
}
```

문서·설정 변경처럼 명시된 검사 경로에 해당하지 않는 변경은 검사를 생략한다. 검사 설정은 저장소에서 관리해 모든 팀원이 동일한 명령을 사용하게 한다.

## 5. 안전 및 오류 처리

다음 작업은 자동 수행하지 않는다.

- `git stash`
- 파일 삭제 또는 `git clean`
- 기존 이슈 삭제
- 사용자가 선택하지 않은 파일 staging
- 인증 토큰 저장
- 테스트 실패 상태에서 일반 제출 진행

필수 사전 조건이 충족되지 않으면 명령을 실패 코드로 종료하고 다음 행동을 안내한다.

- GitHub CLI 미인증: `gh auth login` 안내
- dirty working tree: `git status`, `git diff` 안내
- 기준 브랜치 pull 실패: 원인 출력 후 종료
- 이슈 생성 실패: GitHub 오류 출력 후 브랜치 생성 생략
- 검사 실패: 실패 명령과 로그 출력 후 제출 생략
- staged 파일 없음: VS Code staging 후 `--continue` 재실행 안내
- push 실패: PR 생성 생략
- PR 생성 실패: 생성된 브랜치와 수동 PR 명령 출력

## 6. 테스트 전략

실제 GitHub 저장소를 변경하지 않고 핵심 로직을 검증할 수 있게 Git·GitHub CLI 호출을 작은 실행 계층으로 분리한다.

- slug 생성: 한글, 공백, 특수문자, 연속 구분자 입력 검증
- 브랜치명 생성: 이슈 번호와 작업 타입 형식 검증
- 변경 경로 판별: frontend/backend/문서/복수 영역 검증
- 커밋·PR 본문 생성: 템플릿의 이슈 연결 위치와 테스트 상태 검증
- dirty tree 차단: staged, unstaged, untracked 조합 검증
- 검사 실패 중단: 실패 명령 뒤 Git 변경 명령이 호출되지 않는지 검증
- 실제 GitHub 호출은 mock 실행기와 `--dry-run` 경로로 검증한다.

수동 smoke test는 테스트용 로컬 저장소에서 다음 순서로 수행한다.

1. 깨끗한 `dev`에서 대화형 이슈·브랜치 생성을 확인한다.
2. frontend와 backend 각각의 변경에서 검사 선택을 확인한다.
3. VS Code에서 일부 파일만 staging한 뒤 `--continue`가 staged 파일만 제출하는지 확인한다.
4. 테스트 실패와 dirty tree에서 중단 동작을 확인한다.

## 7. 범위 밖 항목

- GitHub Actions 기반의 이슈·브랜치·PR 생성
- 자동 라벨 및 리뷰어 지정
- 코드 수정 자동화
- PR 병합 및 브랜치 삭제 자동화
- 변경 diff를 이용한 AI 커밋 메시지 생성
- 원격 저장소의 branch protection 설정 변경

## 8. 구현 순서

1. 표준 Python 진입점, 설정 로더, Git·gh 실행 계층 작성
2. 시작 흐름과 템플릿 편집·이슈·브랜치 생성 구현
3. 변경 경로 검사와 테스트 실패 차단 구현
4. VS Code staging을 보존하는 `finish-task`/`--continue` 구현
5. commit·push·PR 생성 및 실패 복구 메시지 구현
6. macOS 래퍼, Windows 실행 안내, `CONTRIBUTING.md` 작성
7. 단위 테스트·mock 테스트·수동 smoke test 실행
