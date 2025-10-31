import {
  type ChangeEvent,
  type FormEvent,
  useCallback,
  useEffect,
  useMemo,
  useState
} from "react";
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  useReactTable
} from "@tanstack/react-table";
import { AreaChart, Card as TremorCard, Title } from "@tremor/react";
import { ShieldCheck } from "lucide-react";

import { Alert } from "./components/ui/alert";
import { Button } from "./components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
import { Input } from "./components/ui/input";
import { Label } from "./components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./components/ui/table";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api";

interface Credentials {
  username: string;
  password: string;
}

interface StatusResponse {
  status: string;
  version: string;
  timestamp: string;
  user: string;
}

interface StatusRecord extends StatusResponse {
  latencyMs: number;
  fetchedAt: string;
}

const MAX_HISTORY = 12;

function useStatusTable(history: StatusRecord[]) {
  const columns = useMemo<ColumnDef<StatusRecord>[]>(
    () => [
      {
        accessorKey: "fetchedAt",
        header: "조회 시각",
        cell: ({ row }) => new Date(row.original.fetchedAt).toLocaleString()
      },
      {
        accessorKey: "status",
        header: "상태",
        cell: ({ row }) => row.original.status
      },
      {
        accessorKey: "version",
        header: "버전",
        cell: ({ row }) => row.original.version
      },
      {
        accessorKey: "latencyMs",
        header: "지연(ms)",
        cell: ({ row }) => row.original.latencyMs.toFixed(1)
      }
    ],
    []
  );

  const table = useReactTable({
    data: history,
    columns,
    getCoreRowModel: getCoreRowModel()
  });

  return table;
}

export default function App() {
  const [credentials, setCredentials] = useState<Credentials>({ username: "", password: "" });
  const [token, setToken] = useState<string>(() => window.localStorage.getItem("token") ?? "");
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [history, setHistory] = useState<StatusRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");

  const table = useStatusTable(history);

  const chartData = useMemo(
    () =>
      history.map((entry) => ({
        time: new Date(entry.fetchedAt).toLocaleTimeString(),
        latency: entry.latencyMs,
        status: entry.status
      })),
    [history]
  );

  const handleChange = (field: keyof Credentials) =>
    (event: ChangeEvent<HTMLInputElement>) => {
      // 입력 필드와 상태를 동기화하여 양방향 바인딩을 구현한다.
      setCredentials((prev) => ({ ...prev, [field]: event.target.value }));
    };

  const handleLogout = useCallback(() => {
    // 보안을 위해 로그아웃 시 로컬 스토리지에 저장된 토큰을 즉시 제거한다.
    window.localStorage.removeItem("token");
    setToken("");
    setStatus(null);
    setHistory([]);
  }, []);

  const fetchStatus = useCallback(async () => {
    if (!token) {
      return;
    }

    setLoading(true);
    setError("");

    try {
      const start = performance.now();
      const response = await fetch(`${API_BASE_URL}/status`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      const end = performance.now();

      if (response.status === 401) {
        throw new Error("세션이 만료되었습니다. 다시 로그인하세요.");
      }

      if (!response.ok) {
        throw new Error("상태 정보를 불러오지 못했습니다.");
      }

      const payload: StatusResponse = await response.json();
      setStatus(payload);
      setHistory((prev) => {
        const next: StatusRecord[] = [
          {
            ...payload,
            latencyMs: end - start,
            fetchedAt: new Date().toISOString()
          },
          ...prev
        ];
        return next.slice(0, MAX_HISTORY);
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : "알 수 없는 오류가 발생했습니다.";
      setError(message);
      handleLogout();
    } finally {
      setLoading(false);
    }
  }, [handleLogout, token]);

  const handleLogin = useCallback(
    async (event: FormEvent<HTMLFormElement>) => {
      event.preventDefault();
      setLoading(true);
      setError("");

      try {
        const body = new URLSearchParams();
        body.append("username", credentials.username);
        body.append("password", credentials.password);

        const response = await fetch(`${API_BASE_URL}/auth/token`, {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded"
          },
          body
        });

        if (!response.ok) {
          throw new Error("로그인에 실패했습니다. 자격 증명을 확인하세요.");
        }

        const data: { access_token: string } = await response.json();
        window.localStorage.setItem("token", data.access_token);
        setToken(data.access_token);
        setCredentials({ username: "", password: "" });
      } catch (err) {
        const message = err instanceof Error ? err.message : "알 수 없는 오류가 발생했습니다.";
        setError(message);
      } finally {
        setLoading(false);
      }
    },
    [credentials.password, credentials.username]
  );

  useEffect(() => {
    // 토큰이 존재하면 대시보드 진입 시 최신 상태를 자동으로 조회한다.
    if (token) {
      fetchStatus().catch(() => {
        // fetchStatus 내에서 오류를 처리하므로 여기서는 무시한다.
      });
    }
  }, [fetchStatus, token]);

  return (
    <div className="mx-auto flex min-h-screen max-w-5xl flex-col gap-6 px-4 py-10">
      <header className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <span className="rounded-full bg-primary/10 p-2 text-primary">
            <ShieldCheck className="h-6 w-6" aria-hidden />
          </span>
          <div>
            <h1 className="text-3xl font-bold">Trading Up 관제 센터</h1>
            <p className="text-muted-foreground">JWT 인증으로 보호되는 내부 모니터링 대시보드</p>
          </div>
        </div>
        {token && (
          <Button onClick={handleLogout} variant="secondary">
            로그아웃
          </Button>
        )}
      </header>

      {!token ? (
        <Card className="max-w-lg">
          <CardHeader>
            <CardTitle>관리자 로그인</CardTitle>
            <CardDescription>환경 변수로 구성된 관리자 계정으로 접속하세요.</CardDescription>
          </CardHeader>
          <CardContent>
            <form className="space-y-4" onSubmit={handleLogin}>
              <div className="space-y-2">
                <Label htmlFor="username">아이디</Label>
                <Input
                  id="username"
                  autoComplete="username"
                  required
                  value={credentials.username}
                  onChange={handleChange("username")}
                  placeholder="admin"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">비밀번호</Label>
                <Input
                  id="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  value={credentials.password}
                  onChange={handleChange("password")}
                  placeholder="********"
                />
              </div>
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? "로그인 중..." : "로그인"}
              </Button>
            </form>
          </CardContent>
          {error && (
            <CardContent>
              <Alert>{error}</Alert>
            </CardContent>
          )}
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <Card className="lg:col-span-2">
            <CardHeader className="flex flex-row items-center justify-between space-y-0">
              <div>
                <CardTitle>서비스 상태</CardTitle>
                <CardDescription>보호된 API에서 최신 지표를 가져옵니다.</CardDescription>
              </div>
              <Button onClick={fetchStatus} disabled={loading}>
                {loading ? "갱신 중..." : "새로 고침"}
              </Button>
            </CardHeader>
            <CardContent className="space-y-6">
              {error && <Alert>{error}</Alert>}
              {status && (
                <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
                  <div className="rounded-lg border bg-muted/30 p-4">
                    <p className="text-sm text-muted-foreground">상태</p>
                    <p className="text-xl font-semibold">{status.status}</p>
                  </div>
                  <div className="rounded-lg border bg-muted/30 p-4">
                    <p className="text-sm text-muted-foreground">버전</p>
                    <p className="text-xl font-semibold">{status.version}</p>
                  </div>
                  <div className="rounded-lg border bg-muted/30 p-4">
                    <p className="text-sm text-muted-foreground">서버 시각</p>
                    <p className="text-xl font-semibold">
                      {new Date(status.timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>
              )}
              <div>
                <Title>응답 지연 추이</Title>
                <TremorCard className="mt-2">
                  <AreaChart
                    data={chartData.slice().reverse()}
                    index="time"
                    categories={["latency"]}
                    colors={["blue"]}
                    yAxisWidth={60}
                    noDataText="수집된 데이터가 없습니다."
                  />
                </TremorCard>
              </div>
            </CardContent>
          </Card>

          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle>최근 조회 이력</CardTitle>
              <CardDescription>최대 {MAX_HISTORY}개의 측정치를 보관합니다.</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  {table.getHeaderGroups().map((headerGroup) => (
                    <TableRow key={headerGroup.id}>
                      {headerGroup.headers.map((header) => (
                        <TableHead key={header.id}>
                          {header.isPlaceholder
                            ? null
                            : flexRender(header.column.columnDef.header, header.getContext())}
                        </TableHead>
                      ))}
                    </TableRow>
                  ))}
                </TableHeader>
                <TableBody>
                  {table.getRowModel().rows.length ? (
                    table.getRowModel().rows.map((row) => (
                      <TableRow key={row.id}>
                        {row.getVisibleCells().map((cell) => (
                          <TableCell key={cell.id}>
                            {flexRender(cell.column.columnDef.cell, cell.getContext())}
                          </TableCell>
                        ))}
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={table.getAllColumns().length} className="text-center">
                        조회 이력이 없습니다.
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
