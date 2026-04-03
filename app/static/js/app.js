// Todo App - Frontend Logic

const API_URL = "/api/todos";

const todoForm = document.getElementById("todo-form");
const todoInput = document.getElementById("todo-input");
const todoList = document.getElementById("todo-list");
const emptyState = document.getElementById("empty-state");
const errorState = document.getElementById("error-state");
const listContainer = document.getElementById("todo-list-container");
const selectedDateLabel = document.getElementById("selected-date-label");
const calMonthLabel = document.getElementById("cal-month-label");
const calDays = document.getElementById("cal-days");

let todos = [];
let selectedDate = toLocalDateStr(new Date());
let calYear = new Date().getFullYear();
let calMonth = new Date().getMonth();
let datesWithTodos = new Set();

// ── 날짜 유틸 ────────────────────────────────────────────

function toLocalDateStr(date) {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

function formatKoreanDate(dateStr) {
  const [y, m, d] = dateStr.split("-").map(Number);
  const date = new Date(y, m - 1, d);
  const days = ["일", "월", "화", "수", "목", "금", "토"];
  return `${y}년 ${m}월 ${d}일 ${days[date.getDay()]}요일`;
}

function isToday(dateStr) {
  return dateStr === toLocalDateStr(new Date());
}

// ── 선택 날짜 라벨 ────────────────────────────────────────

function renderSelectedDateLabel() {
  if (isToday(selectedDate)) {
    selectedDateLabel.textContent = formatKoreanDate(selectedDate);
  } else {
    selectedDateLabel.textContent = formatKoreanDate(selectedDate);
  }
}

// ── 캘린더 ───────────────────────────────────────────────

function renderCalendar() {
  const months = ["1월","2월","3월","4월","5월","6월",
                  "7월","8월","9월","10월","11월","12월"];
  calMonthLabel.textContent = `${calYear}년 ${months[calMonth]}`;

  calDays.textContent = "";

  const firstDay = new Date(calYear, calMonth, 1).getDay();
  const lastDate = new Date(calYear, calMonth + 1, 0).getDate();
  const prevLastDate = new Date(calYear, calMonth, 0).getDate();

  for (let i = firstDay - 1; i >= 0; i--) {
    calDays.appendChild(makeDayCell(prevLastDate - i, calYear, calMonth - 1, true));
  }

  for (let d = 1; d <= lastDate; d++) {
    calDays.appendChild(makeDayCell(d, calYear, calMonth, false));
  }

  const total = firstDay + lastDate;
  const remaining = total % 7 === 0 ? 0 : 7 - (total % 7);
  for (let i = 1; i <= remaining; i++) {
    calDays.appendChild(makeDayCell(i, calYear, calMonth + 1, true));
  }
}

function makeDayCell(day, year, month, otherMonth) {
  const realYear = year + Math.floor(month / 12);
  const realMonth = ((month % 12) + 12) % 12;
  const dateStr = `${realYear}-${String(realMonth + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;

  const cell = document.createElement("div");
  cell.className = [
    "cal-day",
    otherMonth   ? "other-month" : "",
    isToday(dateStr)          ? "today"    : "",
    dateStr === selectedDate  ? "selected" : "",
  ].filter(Boolean).join(" ");

  const numSpan = document.createElement("span");
  numSpan.className = "cal-day-num";
  numSpan.textContent = day;
  cell.appendChild(numSpan);

  if (datesWithTodos.has(dateStr)) {
    const dot = document.createElement("span");
    dot.className = "cal-dot";
    cell.appendChild(dot);
  }

  if (!otherMonth) {
    cell.addEventListener("click", () => selectDate(dateStr));
  }

  return cell;
}

function selectDate(dateStr) {
  selectedDate = dateStr;
  // 선택한 날짜가 현재 보이는 달과 다르면 달도 이동
  const [y, m] = dateStr.split("-").map(Number);
  calYear = y;
  calMonth = m - 1;
  renderCalendar();
  renderSelectedDateLabel();
  fetchTodos();
}

document.getElementById("cal-prev").addEventListener("click", () => {
  calMonth--;
  if (calMonth < 0) { calMonth = 11; calYear--; }
  renderCalendar();
});

document.getElementById("cal-next").addEventListener("click", () => {
  calMonth++;
  if (calMonth > 11) { calMonth = 0; calYear++; }
  renderCalendar();
});

// ── API 통신 ──────────────────────────────────────────────

async function fetchDatesWithTodos() {
  try {
    const res = await fetch(`${API_URL}/dates`);
    if (!res.ok) return;
    const dates = await res.json();
    datesWithTodos = new Set(dates);
    renderCalendar();
  } catch {
    // 점 표시 실패는 무시
  }
}

async function fetchTodos() {
  listContainer.classList.add("loading");
  errorState.hidden = true;
  emptyState.hidden = true;
  todoList.textContent = "";

  try {
    const res = await fetch(`${API_URL}/?date=${selectedDate}`);
    if (!res.ok) throw new Error("서버 오류");
    todos = await res.json();
    renderTodos();
  } catch {
    errorState.hidden = false;
  } finally {
    listContainer.classList.remove("loading");
  }
}

async function addTodo(title) {
  const res = await fetch(API_URL + "/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, due_date: selectedDate }),
  });
  if (!res.ok) throw new Error("추가 실패");
  const todo = await res.json();
  todos.push(todo);
  datesWithTodos.add(selectedDate);
  renderTodos();
  renderCalendar();
}

async function toggleTodo(id, completed) {
  const res = await fetch(`${API_URL}/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ completed }),
  });
  if (!res.ok) throw new Error("토글 실패");
  return res.json();
}

async function deleteTodo(id) {
  const res = await fetch(`${API_URL}/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("삭제 실패");
}

async function updateTodoTitle(id, title) {
  const res = await fetch(`${API_URL}/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });
  if (!res.ok) throw new Error("수정 실패");
  return res.json();
}

// ── 렌더링 ────────────────────────────────────────────────

function renderTodos() {
  todoList.textContent = "";

  if (todos.length === 0) {
    emptyState.hidden = false;
    return;
  }
  emptyState.hidden = true;

  todos.forEach((todo) => todoList.appendChild(createTodoElement(todo)));
}

function createTodoElement(todo) {
  const li = document.createElement("li");
  li.className = "todo-item" + (todo.completed ? " completed" : "");
  li.dataset.id = todo.id;

  const checkbox = document.createElement("div");
  checkbox.className = "todo-checkbox";
  const mark = document.createElement("span");
  mark.className = "todo-checkbox-mark";
  mark.innerHTML = "&#10003;"; // 정적 체크마크 — innerHTML 허용 예외
  checkbox.appendChild(mark);

  const titleSpan = document.createElement("span");
  titleSpan.className = "todo-title";
  titleSpan.textContent = todo.title;

  const deleteBtn = document.createElement("button");
  deleteBtn.className = "todo-delete";
  deleteBtn.setAttribute("aria-label", "삭제");
  deleteBtn.textContent = "×";

  checkbox.addEventListener("click", () => handleToggle(li, todo));
  deleteBtn.addEventListener("click", () => handleDelete(li, todo.id));
  titleSpan.addEventListener("dblclick", () => {
    if (!todo.completed) startEditing(li, todo, titleSpan);
  });

  li.appendChild(checkbox);
  li.appendChild(titleSpan);
  li.appendChild(deleteBtn);
  return li;
}

// ── 핸들러 ───────────────────────────────────────────────

function handleToggle(li, todo) {
  const newCompleted = !todo.completed;
  todo.completed = newCompleted;
  li.classList.toggle("completed", newCompleted);

  toggleTodo(todo.id, newCompleted).then((updated) => {
    todo.completed = updated.completed;
    li.classList.toggle("completed", updated.completed);
  }).catch(() => {
    todo.completed = !newCompleted;
    li.classList.toggle("completed", !newCompleted);
  });
}

function handleDelete(li, id) {
  li.style.maxHeight = li.offsetHeight + "px";
  requestAnimationFrame(() => li.classList.add("removing"));

  li.addEventListener("transitionend", () => {
    li.remove();
    todos = todos.filter((t) => t.id !== id);
    if (todos.length === 0) emptyState.hidden = false;
    fetchDatesWithTodos();
  }, { once: true });

  deleteTodo(id).catch(() => {
    li.classList.remove("removing");
    li.style.maxHeight = "";
  });
}

function startEditing(li, todo, titleSpan) {
  const input = document.createElement("input");
  input.type = "text";
  input.className = "todo-edit-input";
  input.value = todo.title;
  li.replaceChild(input, titleSpan);
  input.focus();
  input.select();

  let saved = false;

  async function save() {
    if (saved) return;
    saved = true;
    const newTitle = input.value.trim();
    if (!newTitle || newTitle === todo.title) {
      li.replaceChild(titleSpan, input);
      return;
    }
    try {
      const updated = await updateTodoTitle(todo.id, newTitle);
      todo.title = updated.title;
      titleSpan.textContent = updated.title;
    } catch {
      titleSpan.textContent = todo.title;
    }
    li.replaceChild(titleSpan, input);
  }

  function cancel() {
    if (saved) return;
    saved = true;
    li.replaceChild(titleSpan, input);
  }

  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") save();
    if (e.key === "Escape") cancel();
  });
  input.addEventListener("blur", save);
}

// ── 폼 제출 ──────────────────────────────────────────────

todoForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const title = todoInput.value.trim();

  if (!title) {
    todoInput.classList.remove("shake");
    void todoInput.offsetWidth;
    todoInput.classList.add("shake");
    todoInput.addEventListener("animationend", () => {
      todoInput.classList.remove("shake");
    }, { once: true });
    return;
  }

  try {
    await addTodo(title);
    todoInput.value = "";
    todoInput.focus();
  } catch {
    // 서버 오류 시 입력 유지
  }
});

// ── 초기화 ───────────────────────────────────────────────

renderSelectedDateLabel();
renderCalendar();
fetchDatesWithTodos();
fetchTodos();
