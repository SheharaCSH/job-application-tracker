const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
import { request } from "./api";
import "./App.css";

const STATUSES = ["Applied", "Interview", "Offer", "Rejected"];

function AuthForm({ onLoggedIn }) {
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    try {
      if (mode === "register") {
        await request("/auth/register", { method: "POST", body: { email, password } });
      }
      const data = await request("/auth/login", {
        method: "POST",
        form: { username: email, password },
      });
      onLoggedIn(data.access_token);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="auth">
      <h1>Job Application Tracker</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password (8+ characters)"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          minLength={8}
          required
        />
        <button type="submit">{mode === "login" ? "Log in" : "Create account"}</button>
      </form>
      {error && <p className="error">{error}</p>}
      <button className="link" onClick={() => setMode(mode === "login" ? "register" : "login")}>
        {mode === "login" ? "No account? Register" : "Have an account? Log in"}
      </button>
    </div>
  );
}

function Board({ token, onLogout }) {
  const [apps, setApps] = useState([]);
  const [company, setCompany] = useState("");
  const [role, setRole] = useState("");
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    try {
      setApps(await request("/applications", { token }));
    } catch (err) {
      if (err.status === 401) onLogout();
      else setError(err.message);
    }
  }, [token, onLogout]);

  useEffect(() => {
    load();
  }, [load]);

  async function addApplication(e) {
    e.preventDefault();
    setError("");
    try {
      await request("/applications", { method: "POST", token, body: { company, role } });
      setCompany("");
      setRole("");
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function changeStatus(id, status) {
    try {
      await request(`/applications/${id}`, { method: "PATCH", token, body: { status } });
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function remove(id) {
    try {
      await request(`/applications/${id}`, { method: "DELETE", token });
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="board-page">
      <header>
        <h1>My Applications</h1>
        <button onClick={onLogout}>Log out</button>
      </header>

      <form className="add" onSubmit={addApplication}>
        <input
          placeholder="Company"
          value={company}
          onChange={(e) => setCompany(e.target.value)}
          required
        />
        <input
          placeholder="Role"
          value={role}
          onChange={(e) => setRole(e.target.value)}
          required
        />
        <button type="submit">Add</button>
      </form>
      {error && <p className="error">{error}</p>}

      <div className="columns">
        {STATUSES.map((status) => {
          const items = apps.filter((a) => a.status === status);
          return (
            <section key={status} className="column">
              <h2>
                {status} <span>{items.length}</span>
              </h2>
              {items.map((a) => (
                <article key={a.id} className="card">
                  <strong>{a.company}</strong>
                  <p>{a.role}</p>
                  <small>{a.applied_date}</small>
                  <div className="actions">
                    <select value={a.status} onChange={(e) => changeStatus(a.id, e.target.value)}>
                      {STATUSES.map((s) => (
                        <option key={s}>{s}</option>
                      ))}
                    </select>
                    <button className="danger" onClick={() => remove(a.id)}>
                      Delete
                    </button>
                  </div>
                </article>
              ))}
            </section>
          );
        })}
      </div>
    </div>
  );
}

function App() {
  const [token, setToken] = useState(() => localStorage.getItem("token"));

  function handleLogin(newToken) {
    localStorage.setItem("token", newToken);
    setToken(newToken);
  }

  const handleLogout = useCallback(() => {
    localStorage.removeItem("token");
    setToken(null);
  }, []);

  return token ? (
    <Board token={token} onLogout={handleLogout} />
  ) : (
    <AuthForm onLoggedIn={handleLogin} />
  );
}

export default App;