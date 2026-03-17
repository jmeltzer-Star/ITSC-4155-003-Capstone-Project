/*
========================================================
USER STORY → FUNCTION MAPPING (Momentum Project)
========================================================

-------------------------------
TASK MANAGEMENT
-------------------------------

User Story: Create Task
- Handles creating a new task with validation
→ form submit event listener
→ validateFutureDate()
→ formatForBackend()

User Story: View Tasks (Task Log)
- Displays all tasks in table format
→ fetchTasks()
→ renderTasks()

User Story: Edit Task
- Allows updating existing tasks
→ openEditForm()
→ editForm submit event listener
→ highlightUpdatedFields()
→ closeEditForm()

User Story: Delete Task
- Removes a task from the system
→ handleDeleteTask()

User Story: Complete Task
- Marks task as completed and allows undo
→ markTaskComplete()
→ undoCompleteTask()

User Story: Sort Tasks
- Sort tasks by selected criteria
→ sortSelect change listener
→ fetchTasks()


-------------------------------
VALIDATION + UTILITIES
-------------------------------

User Story: Date Validation
- Ensures valid and future due dates
→ parseDateInput()
→ validateFutureDate()

User Story: Backend Formatting
- Converts frontend datetime format to backend format
→ formatForBackend()

User Story: UI Messaging
- Handles temporary success/error messages
→ clearCreateMessageAfterDelay()
→ clearEditMessageAfterDelay()


-------------------------------
SCHEDULE SYSTEM
-------------------------------

User Story: Generate Schedule
- Generates schedule based on constraints
→ handleGenerateSchedule()

User Story: View Schedule (Calendar)
- Displays schedule in calendar format
→ renderSchedule()

User Story: Refresh Schedule
- Re-fetch and update schedule view
→ refreshScheduleView()

User Story: Schedule Load Indicator
- Shows how full the schedule is
→ updateScheduleLoad()

User Story: Schedule Insights (AI Summary)
- Provides human-readable schedule explanation
→ generateScheduleSummary()

User Story: Save Schedule Preferences
- Persists schedule settings locally
→ loadSavedScheduleSettings()
→ localStorage usage in handleGenerateSchedule()

User Story: Load Saved Schedule
- Loads previously saved schedule on refresh
→ loadSavedSchedule()


-------------------------------
SCHEDULE CONFLICT DETECTION
-------------------------------

User Story: Detect Conflicts
- Detect overlapping scheduled tasks
→ parseTimeToMinutes()
→ findScheduleConflicts()
→ detectAllScheduleConflicts()

User Story: Display Conflict Alerts
- Shows conflicts in UI and highlights tasks
→ renderConflictAlerts()
→ renderSchedule() (conflict styling)


-------------------------------
DASHBOARD
-------------------------------

User Story: View Dashboard Metrics
- Shows totals, progress, and recent tasks
→ loadDashboard()

User Story: Progress Tracking
- Displays completion percentage visually
→ loadDashboard() (progressFill, progressPercent)


-------------------------------
EXTRA FEATURES / UX
-------------------------------

User Story: Daily Motivation Quote
- Displays a motivational quote
→ loadQuote()

User Story: Intro Overlay
- Displays intro screen on first load
→ closeIntroOverlay()
→ introContinueBtn listener

User Story: Interactive Visual (Momentum Orb)
- 3D animated UI element
→ initMomentumOrb()


========================================================
ARCHITECTURE NOTE
========================================================
- API Layer: fetchTasks(), handleGenerateSchedule(), loadDashboard()
- Rendering Layer: renderTasks(), renderSchedule()
- Logic Layer: conflict detection, validation, schedule calculations
- UI Layer: messages, highlights, animations

========================================================
*/


// --- Task Creation Elements ---
const form = document.getElementById("taskForm");
const msg = document.getElementById("message");
const tbody = document.getElementById("taskTableBody");
const sortSelect = document.getElementById("sortSelect");

// --- Task Editing Elements ---
const editSection = document.getElementById("editTaskSection");
const editForm = document.getElementById("editTaskForm");
const editTaskId = document.getElementById("editTaskId");
const editTitle = document.getElementById("editTitle");
const editDueDate = document.getElementById("editDueDate");
const editPriority = document.getElementById("editPriority");
const editStatus = document.getElementById("editStatus");
const editMessage = document.getElementById("editMessage");
const editDueDateMsg = document.getElementById("editDueDateMsg");
const cancelEditBtn = document.getElementById("cancelEditBtn");
const editDurationMinutes = document.getElementById("editDurationMinutes");
const editEffortLevel = document.getElementById("editEffortLevel");
const editStartAfter = document.getElementById("editStartAfter");
const editCategory = document.getElementById("editCategory");

// --- Schedule / Intelligence Elements ---
const scheduleLoadFill = document.getElementById("scheduleLoadFill");
const scheduleLoadPercent = document.getElementById("scheduleLoadPercent");
const scheduleLoadText = document.getElementById("scheduleLoadText");
const scheduleSummary = document.getElementById("scheduleSummary");
// --- Intro / Landing Elements ---
const introOverlay = document.getElementById("introOverlay");
const introContinueBtn = document.getElementById("introContinueBtn");


/* ========================================================
   SECTION: Shared State
   Purpose: Store temporary values used across actions.
======================================================== */




let originalTaskData = null;



/* ========================================================
   SECTION: Utility Functions
   Purpose: Small reusable helpers for formatting dates,
   times, and keys used by tasks and schedules.
======================================================== */

//Method which formats our Backend Data into the Format Which we See On Our Schedule and Task List 
function formatForBackend(datetimeLocalValue) {
  return datetimeLocalValue.includes("T")
    ? datetimeLocalValue.replace("T", " ")
    : datetimeLocalValue;
}

/* 

Feature: Date Parsing and Future Date Validation

Purpose

Handles task due date validation by converting user input into a JavaScript Date object and ensuring the selected date is valid and in the future before allowing a task to be created or updated.

Function #1: parseDateInput()

Purpose:
Converts a date string from a form input into a usable JavaScript Date object.

What it handles:
	•	Supports HTML datetime-local inputs (format includes "T")
	•	Extracts year, month, day, hour, and minute
	•	Returns a properly formatted Date object
	•	Returns null if no value is provided



Function: validateFutureDate()

Purpose:
Ensures that the user selects a valid due date that is in the future before submitting a task.

Validation Checks
	1.	Ensures the field is not empty
	2.	Ensures the date format is valid
	3.	Ensures the selected date is later than the current time

User Feedback
If validation fails, an inline error message is shown next to the input field.

Possible Messages
	•	"Required"
	•	"Invalid date"
	•	"Due date must be in the future."






*/



function parseDateInput(value) {
  if (!value) return null;

  if (value.includes("T")) {
    const [datePart, timePart] = value.split("T");
    const [y, m, d] = datePart.split("-").map(Number);
    const [h = 0, min = 0] = (timePart || "").split(":").map(Number);
    return new Date(y, m - 1, d, h, min);
  }

  return new Date(value);
}

function formatLocalDateKey(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function detectScheduleConflicts(tasks) {
  const conflicts = new Set();

  for (let i = 0; i < tasks.length; i++) {
    for (let j = i + 1; j < tasks.length; j++) {

      const startA = new Date(tasks[i].scheduled_start);
      const endA = new Date(tasks[i].scheduled_end);

      const startB = new Date(tasks[j].scheduled_start);
      const endB = new Date(tasks[j].scheduled_end);

      if (startA < endB && endA > startB) {
        conflicts.add(tasks[i].id);
        conflicts.add(tasks[j].id);
      }
    }
  }

  return conflicts;
}



/* ========================================================
   SECTION: Validation
   Purpose: Validate required task inputs before creating
   or editing a task.
======================================================== */

function isTaskOverdue(task) { 
  if (!task.due_date || task.status === "Completed") {
    return false;
  }
  const dueDate = new Date(task.due_date);
  if (isNaN(dueDate.getTime())) {
    return false; // Invalid date
  }
  const now = new Date();
  return dueDate < now;
}


function validateFutureDate(inputValue, inlineMsgEl) {
  inlineMsgEl.textContent = "";

  if (!inputValue) {
    inlineMsgEl.textContent = "Required";
    return false;
  }

  const dateObj = parseDateInput(inputValue);
  if (!dateObj || isNaN(dateObj.getTime())) {
    inlineMsgEl.textContent = "Invalid date";
    return false;
  }

  const now = new Date();
  if (dateObj <= now) {
    inlineMsgEl.textContent = "Due date must be in the future.";
    return false;
  }

  return true;
}

/* ========================================================
   SECTION: UI Feedback Helpers
   Purpose: Clear temporary success and error messages after
   task creation or editing actions.
======================================================== */



function clearCreateMessageAfterDelay(delay = 5000) {
  setTimeout(() => {
    msg.textContent = "";
    msg.className = "message";
  }, delay);
}

function clearEditMessageAfterDelay() {
  setTimeout(() => {
    editMessage.textContent = "";
    editMessage.className = "message";
  }, 5000);
}
/* ========================================================
   SECTION: Task Data Loading and Rendering
   Purpose: Fetch tasks from the backend and render them
   into the Task Log table.
======================================================== */






/*
Purpose:
Load tasks from the backend API, optionally applying the
selected sort option, then render them in the Task Log.
*/
async function fetchTasks() {
  if (!tbody || !sortSelect) return;
  try {
    const sort = sortSelect.value;
    const url = sort ? `/api/tasks?sort=${encodeURIComponent(sort)}` : "/api/tasks";

    const res = await fetch(url);
    const tasks = await res.json();

    if (!res.ok) {
      throw new Error(tasks.error || "Failed to load tasks.");
    }

    renderTasks(tasks);
  } catch (err) {
    tbody.innerHTML = `
      <tr>
        <td colspan="5">Failed to load tasks.</td>
      </tr>
    `;
    console.error(err);
  }
}






/*
Purpose:
Render task rows into the Task Log table, including status,
priority, meta pills, and action buttons.
*/
function generateScheduleSummary(schedule) {
  if (!scheduleSummary) return;

  const allTasks = Object.values(schedule).flat();
  const totalTasks = allTasks.length;
  const totalDaysUsed = Object.keys(schedule).filter(day => schedule[day].length > 0).length;

  if (!totalTasks) {
    scheduleSummary.textContent = "No schedule insights are available because no tasks were scheduled.";
    return;
  }

  const highPriorityCount = allTasks.filter(task => task.priority === "High").length;
  const highEffortCount = allTasks.filter(task => task.effort_level === "High").length;

  let busiestDayCount = 0;
  Object.values(schedule).forEach(dayTasks => {
    if (dayTasks.length > busiestDayCount) {
      busiestDayCount = dayTasks.length;
    }
  });

  const summaries = [];

  if (highPriorityCount > 0) {
    summaries.push("This schedule focuses on urgent tasks first.");
  }

  if (highEffortCount > 0) {
    summaries.push("High-effort tasks are placed earlier where possible.");
  }

  if (totalDaysUsed >= 2) {
    summaries.push("Your workload is spread across multiple days for better balance.");
  } else {
    summaries.push("Your workload is concentrated into a short time window.");
  }

  if (busiestDayCount >= 4) {
    summaries.push("One or more days are heavily loaded, so consider increasing the schedule range if needed.");
  } else if (busiestDayCount >= 2) {
    summaries.push("Your workload is moderately balanced this week.");
  } else {
    summaries.push("Your current schedule load is light and manageable.");
  }

  scheduleSummary.textContent = summaries.join(" ");
}


/*
Purpose:
Render task rows into the Task Log table, including status,
priority, meta pills, and action buttons.
*/

function renderTasks(tasks) {
  tbody.innerHTML = "";

  if (!tasks.length) {
    tbody.innerHTML = `
      <tr>
        <td colspan="5">No tasks found.</td>
      </tr>
    `;
    return;
  }

  tasks.forEach((task) => {
    const row = document.createElement("tr");
    row.dataset.taskId = task.id;

    let statusClass = "status-pending";
    if (task.status === "In Progress") statusClass = "status-progress";
    if (task.status === "Completed") statusClass = "status-completed";

    if (task.status === "Completed") {
      row.classList.add("task-completed-row");
    }

    let priorityClass = "priority-low";
    if (task.priority === "High") priorityClass = "priority-high";
    if (task.priority === "Medium") priorityClass = "priority-medium";

    const formattedStartAfter = task.start_after
      ? task.start_after
      : "No restriction";

    row.innerHTML = `
      <td>
        <div class="task-title-cell">
          <div class="task-main-title">${task.title}</div>
          <div class="task-meta">
            <span class="task-meta-pill">${task.category}</span>
            <span class="task-meta-pill">${task.duration_minutes} min</span>
            <span class="task-meta-pill">${task.effort_level} Effort</span>
            <span class="task-meta-pill">Start: ${formattedStartAfter}</span>
          </div>
        </div>
      </td>
      <td><span class="status-badge ${statusClass}">${task.status}</span></td>
      <td>${task.due_date}</td>
      <td><span class="priority-pill ${priorityClass}">${task.priority}</span></td>
      <td class="actions-cell">
      <button type="button" class="edit-btn">Edit</button>
      <button type="button" class="delete-btn">Delete</button>
      ${task.status !== "Completed" ? '<button type="button" class="complete-btn">Complete</button>' : ""}
      </td>
    `;

    row.querySelector(".edit-btn").addEventListener("click", () => {
      openEditForm(task);
    });

    row.querySelector(".delete-btn").addEventListener("click", () => {
      handleDeleteTask(task.id, task.title);
    });

    const completeBtn = row.querySelector(".complete-btn");
    if (completeBtn) {
      completeBtn.addEventListener("click", () => {
        markTaskComplete(task);
      });
    }

    tbody.appendChild(row);
  });
}



/* ========================================================
   SECTION: Task Completion Workflow
   Purpose: Mark tasks as completed, support undo, and keep
   the task list, dashboard, and schedule in sync.
======================================================== */



async function markTaskComplete(task) {
  const previousStatus = task.status;

  try {
    const res = await fetch(`/api/tasks/${task.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title: task.title,
        due_date: task.due_date,
        priority: task.priority,
        status: "Completed",
        duration_minutes: task.duration_minutes,
        effort_level: task.effort_level,
        start_after: task.start_after,
        category: task.category
      })
    });

    const data = await res.json();

    if (!res.ok) {
      if (msg) {
        msg.textContent = data.error || "Failed to mark task as completed.";
        msg.className = "message error";
        clearCreateMessageAfterDelay();
      }
      return;
    }

    await fetchTasks();
    
    await loadDashboard();

    if (msg) {
      msg.className = "message success";
      msg.innerHTML = `
        Task marked as completed.
        <a href="#" id="undoCompleteLink">Undo</a>
      `;
    }

    const undoLink = document.getElementById("undoCompleteLink");
    if (undoLink) {
      undoLink.addEventListener("click", async (e) => {
        e.preventDefault();
        await undoCompleteTask(task, previousStatus);
      });
    }

    clearCreateMessageAfterDelay();
  } catch (err) {
    console.error(err);

    if (msg) {
      msg.textContent = "Failed to mark task as completed.";
      msg.className = "message error";
      clearCreateMessageAfterDelay();
    }
  }
}

async function undoCompleteTask(task, previousStatus = "Pending") {
  try {
    const res = await fetch(`/api/tasks/${task.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title: task.title,
        due_date: task.due_date,
        priority: task.priority,
        status: previousStatus,
        duration_minutes: task.duration_minutes,
        effort_level: task.effort_level,
        start_after: task.start_after,
        category: task.category
      })
    });

    const data = await res.json();

    if (!res.ok) {
      if (msg) {
        msg.textContent = data.error || "Failed to undo completion.";
        msg.className = "message error";
        clearCreateMessageAfterDelay();
      }
      return;
    }

    if (msg) {
      msg.textContent = "Task restored.";
      msg.className = "message success";
      clearCreateMessageAfterDelay();
    }

    await fetchTasks();
    loadDashboard();
    await refreshScheduleView();
  } catch (err) {
    console.error(err);
    if (msg) {
      msg.textContent = "Failed to undo completion.";
      msg.className = "message error";
      clearCreateMessageAfterDelay();
    }
  }
}


/* ========================================================
   SECTION: Edit Feedback / Highlighting
   Purpose: Visually highlight which task fields changed
   after a successful update.
======================================================== */



function highlightUpdatedFields(id, updatedTask) {
  const row = document.querySelector(`tr[data-task-id="${id}"]`);
  if (!row || !originalTaskData) return;

  const cells = row.children;

  if (updatedTask.title !== originalTaskData.title) {
    cells[0].classList.add("updated-field");
  }

  if (updatedTask.status !== originalTaskData.status) {
    cells[1].classList.add("updated-field");
  }

  if (updatedTask.due_date !== originalTaskData.due_date) {
    cells[2].classList.add("updated-field");
  }

  if (updatedTask.priority !== originalTaskData.priority) {
    cells[3].classList.add("updated-field");
  }

  if (
    updatedTask.duration_minutes !== originalTaskData.duration_minutes ||
    updatedTask.effort_level !== originalTaskData.effort_level ||
    updatedTask.start_after !== originalTaskData.start_after ||
    updatedTask.category !== originalTaskData.category
  ) {
    cells[0].classList.add("updated-field");
  }

  row.classList.add("updated-row");

  setTimeout(() => {
    row.classList.remove("updated-row");
    Array.from(cells).forEach(cell => cell.classList.remove("updated-field"));
  }, 2500);
}


/* ========================================================
   SECTION: Task Creation
   Purpose: Read form input, validate it, send the create
   request, and refresh dependent UI sections.
======================================================== */

/*
User Story #1: Create Task

As a user, I want to create a task with priority, effort,
duration, and category so it can be stored and later scheduled.
*/



// ---------- Create Task ----------
if (form) {
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    if (msg) {
      msg.textContent = "";
      msg.className = "message";
    }

    const title = document.getElementById("title")?.value.trim() || "";
    const dueInput = document.getElementById("dueDate")?.value.trim() || "";
    const priority = document.getElementById("priority")?.value || "Medium";
    const durationMinutes = document.getElementById("durationMinutes")?.value || 60;
    const effortLevel = document.getElementById("effortLevel")?.value || "Medium";
    const startAfterInput = document.getElementById("startAfter")?.value.trim() || "";
    const category = document.getElementById("category")?.value || "General";
    const dueDateMsg = document.getElementById("dueDateMsg");

    if (dueDateMsg) {
      dueDateMsg.textContent = "";
    }

    if (!validateFutureDate(dueInput, dueDateMsg)) {
      return;
    }

    const due_date = formatForBackend(dueInput);
    const start_after = startAfterInput ? formatForBackend(startAfterInput) : null;

    if (!title || !due_date) {
      if (msg) {
        msg.textContent = "Title and due date are required.";
        msg.className = "message error";
      }
      return;
    }

    try {
      console.log("Page URL:", window.location.href);

      const res = await fetch("/api/tasks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title,
          due_date,
          priority,
          duration_minutes: Number(durationMinutes),
          effort_level: effortLevel,
          start_after,
          category
        })
      });

      const data = await res.json();

      if (!res.ok) {
        if (msg) {
          msg.textContent = data.error || "Failed to create task.";
          msg.className = "message error";
        }
        return;
      }

      form.reset();

      if (dueDateMsg) {
        dueDateMsg.textContent = "";
      }

      if (msg) {
        msg.textContent = "✓ Task created successfully!";
        msg.className = "message success";
      }

      await fetchTasks();
      await refreshScheduleView();
      clearCreateMessageAfterDelay();
    } catch (err) {
      console.error(err);
      if (msg) {
        msg.textContent = "Failed to create task.";
        msg.className = "message error";
      }
    }
  });
}


/* ========================================================
   SECTION: Schedule Analytics / Intelligence
   Purpose: Calculate schedule load and generate lightweight
   scheduling insights shown in the schedule view.
======================================================== */





/*
Purpose:
Calculate schedule capacity usage based on selected range and
max tasks per day, then update the progress bar UI.
*/

function updateScheduleLoad(schedule) {
  if (!scheduleLoadFill || !scheduleLoadPercent || !scheduleLoadText) return;

  const selectedDays = scheduleRange ? Number(scheduleRange.value) : 7;
  const maxPerDay = maxTasksPerDay ? Number(maxTasksPerDay.value) : 4;

  const totalSlots = selectedDays * maxPerDay;

  let scheduledCount = 0;
  Object.values(schedule).forEach(dayTasks => {
    scheduledCount += dayTasks.length;
  });

  const loadPercent = totalSlots > 0
    ? Math.round((scheduledCount / totalSlots) * 100)
    : 0;

  scheduleLoadFill.style.width = `${loadPercent}%`;
  scheduleLoadPercent.textContent = `${loadPercent}%`;
  scheduleLoadText.textContent = `${scheduledCount} / ${totalSlots} slots used`;
}


/* USER STORY #3: Edit Story */


/* ========================================================
   SECTION: Task Editing
   Purpose: Open the edit form, preload task data, submit
   updates, and refresh the UI after changes.
   User Story: Edit User Story 
======================================================== */

/*
Purpose:
Reveal the edit form and prefill it with the selected task's
current values so the user can make updates.
*/
function openEditForm(task) {
  editSection.style.display = "block";

  editTaskId.value = task.id;
  editTitle.value = task.title;
  editDueDate.value = task.due_date.replace(" ", "T");
  editPriority.value = task.priority;
  editStatus.value = task.status;
  editDurationMinutes.value = task.duration_minutes ?? 60;
  editEffortLevel.value = task.effort_level ?? "Medium";
  editStartAfter.value = task.start_after ? task.start_after.replace(" ", "T") : "";
  editCategory.value = task.category ?? "General";

  originalTaskData = { ...task };

  editMessage.textContent = "";
  editMessage.className = "message";
  editDueDateMsg.textContent = "";

  editSection.scrollIntoView({ behavior: "smooth", block: "start" });
}


/*
Purpose:
Hide the edit form, clear temporary edit messages, and reset
the stored original task data.
*/
function closeEditForm() {
  editSection.style.display = "none";
  editForm.reset();
  editTaskId.value = "";
  editMessage.textContent = "";
  editMessage.className = "message";
  editDueDateMsg.textContent = "";
  originalTaskData = null;
}


/*  USER STORY #4: Delete Task */





/* ========================================================
   SECTION: Task Deletion
   Purpose: Confirm deletion, remove the task from the backend,
   and refresh the task and schedule views.
======================================================== */






/*
User Story: Delete Task

As a user, I want to remove tasks I no longer need so my task
list stays clean and relevant.
*/
async function handleDeleteTask(taskId, taskTitle) {
  const confirmed = window.confirm(`Are you sure you want to delete "${taskTitle}"?`);

  if (!confirmed) {
    return;
  }

  try {
    const res = await fetch(`/api/tasks/${taskId}`, {
      method: "DELETE"
    });

    const data = await res.json();

    if (!res.ok) {
      msg.textContent = data.error || "Task could not be deleted.";
      msg.className = "message error";
      clearCreateMessageAfterDelay();
      return;
    }

    msg.textContent = "Task deleted successfully.";
    msg.className = "message success";

    await fetchTasks();
    await refreshScheduleView();
    clearCreateMessageAfterDelay();
  } catch (err) {
    msg.textContent = "Task could not be deleted.";
    msg.className = "message error";
    console.error(err);
    clearCreateMessageAfterDelay();
  }
}




/* ========================================================
   SECTION: Task Editing
   Purpose: Open the edit form, preload task data, submit
   updates, and refresh the UI after changes.
======================================================== */


if (editForm) {
  editForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    editMessage.textContent = "";
    editMessage.className = "message";
    editDueDateMsg.textContent = "";

    const id = editTaskId.value;
    const title = editTitle.value.trim();
    const dueInput = editDueDate.value.trim();
    const priority = editPriority.value;
    const status = editStatus.value;
    const durationMinutes = editDurationMinutes.value;
    const effortLevel = editEffortLevel.value;
    const startAfterInput = editStartAfter.value.trim();
    const category = editCategory.value;

    if (!title) {
      editMessage.textContent = "Title is required.";
      editMessage.className = "message error";
      return;
    }

    if (!validateFutureDate(dueInput, editDueDateMsg)) {
      return;
    }

    const due_date = formatForBackend(dueInput);
    const start_after = startAfterInput ? formatForBackend(startAfterInput) : null;

    try {
      const res = await fetch(`/api/tasks/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title,
          due_date,
          priority,
          status,
          duration_minutes: Number(durationMinutes),
          effort_level: effortLevel,
          start_after,
          category
        })
      });

      const data = await res.json();

      if (!res.ok) {
        editMessage.textContent = data.error || "Task update failed.";
        editMessage.className = "message error";
        return;
      }

      editMessage.textContent = "✓ Task updated successfully!";
      editMessage.className = "message success";

      const updatedTask = {
        id: Number(id),
        title,
        due_date,
        priority,
        status,
        duration_minutes: Number(durationMinutes),
        effort_level: effortLevel,
        start_after,
        category
      };

      await fetchTasks();
      await refreshScheduleView();
      highlightUpdatedFields(id, updatedTask);
      clearEditMessageAfterDelay();

      setTimeout(() => {
        closeEditForm();
      }, 800);
    } catch (err) {
      editMessage.textContent = "Task update failed.";
      editMessage.className = "message error";
      console.error(err);
    }
  });
}

if (cancelEditBtn) {
  cancelEditBtn.addEventListener("click", closeEditForm);
}

// ---------- Sorting ----------
if (sortSelect) {
  sortSelect.addEventListener("change", fetchTasks);
}




/** User Story #6: Schedule Generation  */





/* ========================================================
   SECTION: Schedule View References
   Purpose: Cache schedule page controls and output areas.
======================================================== */



const generateScheduleBtn = document.getElementById("generateScheduleBtn");
const scheduleMessage = document.getElementById("scheduleMessage");
const scheduleOutput = document.getElementById("scheduleOutput");
const scheduleRange = document.getElementById("scheduleRange");
const maxTasksPerDay = document.getElementById("maxTasksPerDay");









/*
========================================================
Function: Render Schedule

Purpose:
Displays the generated schedule on the calendar view.

What it does:
1. Creates a visual card for each day in the schedule.
2. Displays scheduled tasks with time ranges.
3. Shows priority, effort level, and status.
4. Marks today's schedule visually.
5. Displays empty messages for days without tasks.

Result:
Users can easily see how their tasks are distributed
across the upcoming days.
========================================================
*/




function renderSchedule(schedule) {
  if (!scheduleOutput) return;

  const selectedDays = scheduleRange ? Number(scheduleRange.value) : 7;
  const today = new Date();
  const todayString = formatLocalDateKey(today);

  const allConflicts = detectAllScheduleConflicts(schedule);
  const conflictingTaskIds = new Set();

  allConflicts.forEach(conflict => {
    conflictingTaskIds.add(conflict.firstTaskId);
    conflictingTaskIds.add(conflict.secondTaskId);
  });

  const conflictOutput = document.getElementById("conflictOutput");
  if (conflictOutput) {
    if (allConflicts.length > 0) {
      conflictOutput.innerHTML = `<p class="message error">⚠ Schedule conflict detected.</p>`;
    } else {
      conflictOutput.innerHTML = `<p>No conflicts detected.</p>`;
    }
  }

  const startHour = 8;
  const endHour = 18;
  const totalHours = endHour - startHour;
  const hourHeight = 72; // px per hour
  const gridHeight = totalHours * hourHeight;

  scheduleOutput.innerHTML = `
    <div class="calendar-shell">
      <div class="calendar-time-column" id="calendarTimeColumn"></div>
      <div class="calendar-days-grid" id="calendarDaysGrid"></div>
    </div>
  `;

  const timeColumn = document.getElementById("calendarTimeColumn");
  const daysGrid = document.getElementById("calendarDaysGrid");

  for (let hour = startHour; hour <= endHour; hour++) {
    const timeLabel = document.createElement("div");
    timeLabel.className = "calendar-time-label";

    const displayHour = hour === 12 ? 12 : hour % 12 || 12;
    const suffix = hour < 12 ? "AM" : "PM";
    timeLabel.textContent = `${displayHour}:00 ${suffix}`;

    if (hour < endHour) {
      timeLabel.style.height = `${hourHeight}px`;
    }

    timeColumn.appendChild(timeLabel);
  }

  let hasAnyTasks = false;

  for (let i = 0; i < selectedDays; i++) {
    const currentDate = new Date();
    currentDate.setDate(today.getDate() + i);

    const dayKey = formatLocalDateKey(currentDate);
    const tasksForDay = schedule[dayKey] || [];

    const dayColumn = document.createElement("div");
    dayColumn.className = "calendar-day-column";
    if (dayKey === todayString) {
      dayColumn.classList.add("today");
    }

    const header = document.createElement("div");
    header.className = "calendar-day-header";
    header.innerHTML = `
      <strong>${currentDate.toLocaleDateString(undefined, { weekday: "short" })}</strong>
      <span>${currentDate.toLocaleDateString(undefined, {
        month: "short",
        day: "numeric",
        year: "numeric"
      })}</span>
    `;
    dayColumn.appendChild(header);

    const body = document.createElement("div");
    body.className = "calendar-day-body";
    body.style.height = `${gridHeight}px`;

    for (let h = 0; h < totalHours; h++) {
      const line = document.createElement("div");
      line.className = "calendar-hour-line";
      line.style.top = `${h * hourHeight}px`;
      body.appendChild(line);
    }

    if (!tasksForDay.length) {
      const emptyText = document.createElement("p");
      emptyText.className = "calendar-day-empty";
      emptyText.textContent = "No tasks scheduled.";
      body.appendChild(emptyText);
    } else {
      hasAnyTasks = true;

      tasksForDay.forEach((task) => {
        let statusClass = "status-pending";
        if (task.status === "In Progress") statusClass = "status-progress";
        if (task.status === "Completed") statusClass = "status-completed";

        let priorityClass = "priority-low";
        if (task.priority === "High") priorityClass = "priority-high";
        if (task.priority === "Medium") priorityClass = "priority-medium";

        const startMinutes = parseTimeToMinutes(task.scheduled_start);
        const endMinutes = parseTimeToMinutes(task.scheduled_end);

        const top = ((startMinutes - startHour * 60) / 60) * hourHeight;
        const height = ((endMinutes - startMinutes) / 60) * hourHeight;

        const taskBlock = document.createElement("div");
        taskBlock.className = "calendar-event-block";

        if (conflictingTaskIds.has(task.id)) {
          taskBlock.classList.add("conflict-task");
        }

        taskBlock.style.top = `${top}px`;
        taskBlock.style.height = `${Math.max(height, 54)}px`;
        if (height < 90) {
          taskBlock.classList.add("compact");
        }
        
        if (height < 68) {
          taskBlock.classList.add("micro");
        }

        taskBlock.innerHTML = `
          ${conflictingTaskIds.has(task.id) ? '<div class="conflict-label">CONFLICT</div>' : ""}
          <div class="calendar-event-time">${task.scheduled_start} – ${task.scheduled_end}</div>
          <div class="calendar-event-title">${task.title}</div>
          <div class="calendar-event-meta">
            <span class="status-badge ${statusClass}">${task.status}</span>
            <span class="priority-pill ${priorityClass}">${task.priority}</span>
          </div>
          <div class="calendar-event-meta secondary">
            <span class="task-meta-pill">${task.effort_level} Effort</span>
            <span class="task-meta-pill">${task.category}</span>
          </div>
        `;

        body.appendChild(taskBlock);
      });
    }

    dayColumn.appendChild(body);
    daysGrid.appendChild(dayColumn);
  }

  if (!hasAnyTasks && scheduleMessage) {
    scheduleMessage.textContent = "No tasks available to schedule.";
    scheduleMessage.className = "message error";
  }
}



/**Extra Design Feature -- Loading Quote */

async function loadQuote() {
  const quoteEl = document.getElementById("dailyQuote");

  if (!quoteEl) return;

  try {
    const res = await fetch("https://api.quotable.io/random");
    const data = await res.json();

    quoteEl.textContent = `"${data.content}" — ${data.author}`;
  } catch (err) {
    console.error(err);
    quoteEl.textContent = "Stay focused. Keep building momentum.";
  }
}


/* USER STORY #5: AUTO Re-Fresh Storuy  */

async function refreshScheduleView() {
  if (!scheduleOutput) return;

  const savedGenerated = localStorage.getItem("momentumScheduleGenerated");
  if (savedGenerated !== "true") {
    scheduleOutput.innerHTML = "<p>No scheduled tasks available.</p>";
    return;
  }

  const days = scheduleRange
    ? Number(scheduleRange.value || localStorage.getItem("momentumScheduleRange") || 7)
    : 7;

  const max_tasks_per_day = maxTasksPerDay
    ? Number(maxTasksPerDay.value || localStorage.getItem("momentumMaxTasksPerDay") || 4)
    : 4;

  try {
    const res = await fetch("/api/schedule", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ days, max_tasks_per_day })
    });

    const data = await res.json();

    if (!res.ok) {
      scheduleOutput.innerHTML = "<p>No scheduled tasks available.</p>";

      if (scheduleMessage) {
        scheduleMessage.textContent = data.error || "Failed to refresh schedule.";
        scheduleMessage.className = "message error";
      }

      if (scheduleOutput) {
        scheduleOutput.innerHTML = "<p>No scheduled tasks available.</p>";
      }

      if (scheduleLoadFill) scheduleLoadFill.style.width = "0%";
      if (scheduleLoadPercent) scheduleLoadPercent.textContent = "0%";
      if (scheduleLoadText) scheduleLoadText.textContent = "0 / 0 slots used";
      if (scheduleSummary) {
        scheduleSummary.textContent = "No schedule insights are available.";
      }
      if (conflictOutput) {
        conflictOutput.innerHTML = "<p>No conflicts detected.</p>";
      }

      return;
    }

    const scheduleData = data.schedule || {};
    const hasScheduledTasks = Object.values(scheduleData).some(day => day.length > 0);

    if (!hasScheduledTasks) {
      scheduleOutput.innerHTML = "<p>No scheduled tasks available.</p>";

      if (scheduleLoadFill) scheduleLoadFill.style.width = "0%";
      if (scheduleLoadPercent) scheduleLoadPercent.textContent = "0%";
      if (scheduleLoadText) scheduleLoadText.textContent = "0 / 0 slots used";
      if (scheduleSummary) {
        scheduleSummary.textContent = "No schedule insights are available because no tasks were scheduled.";
      }
      if (conflictOutput) {
        conflictOutput.innerHTML = "<p>No conflicts detected.</p>";
      }

      return;
    }

    renderSchedule(scheduleData);
    updateScheduleLoad(scheduleData);
    generateScheduleSummary(scheduleData);

    const conflicts = detectAllScheduleConflicts(scheduleData);
    renderConflictAlerts(conflicts);
  } catch (err) {
    console.error(err);

    if (scheduleMessage) {
      scheduleMessage.textContent = "Failed to refresh schedule.";
      scheduleMessage.className = "message error";
    }

    if (scheduleOutput) {
      scheduleOutput.innerHTML = "<p>No scheduled tasks available.</p>";
    }
  }
}



/*User Story #5: Auto Refresh Story */

async function refreshScheduleView() {
  if (!scheduleOutput) return;

  const savedGenerated = localStorage.getItem("momentumScheduleGenerated");
  if (savedGenerated !== "true") {
    scheduleOutput.innerHTML = "<p>No scheduled tasks available.</p>";
    return;
  }

  const days = scheduleRange
    ? Number(scheduleRange.value || localStorage.getItem("momentumScheduleRange") || 7)
    : 7;

  const max_tasks_per_day = maxTasksPerDay
    ? Number(maxTasksPerDay.value || localStorage.getItem("momentumMaxTasksPerDay") || 4)
    : 4;

  try {
    const res = await fetch("/api/schedule", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ days, max_tasks_per_day })
    });

    const data = await res.json();

    if (!res.ok) {
      scheduleOutput.innerHTML = "<p>No scheduled tasks available.</p>";

      if (scheduleMessage) {
        scheduleMessage.textContent = data.error || "Failed to refresh schedule.";
        scheduleMessage.className = "message error";
      }

      if (scheduleLoadFill) scheduleLoadFill.style.width = "0%";
      if (scheduleLoadPercent) scheduleLoadPercent.textContent = "0%";
      if (scheduleLoadText) scheduleLoadText.textContent = "0 / 0 slots used";
      if (scheduleSummary) {
        scheduleSummary.textContent = "No schedule insights are available.";
      }
      if (conflictOutput) {
        conflictOutput.innerHTML = "<p>No conflicts detected.</p>";
      }

      return;
    }

    const scheduleData = data.schedule || {};
    const hasScheduledTasks = Object.values(scheduleData).some(day => day.length > 0);

    if (!hasScheduledTasks) {
      scheduleOutput.innerHTML = "<p>No scheduled tasks available.</p>";

      if (scheduleLoadFill) scheduleLoadFill.style.width = "0%";
      if (scheduleLoadPercent) scheduleLoadPercent.textContent = "0%";
      if (scheduleLoadText) scheduleLoadText.textContent = "0 / 0 slots used";
      if (scheduleSummary) {
        scheduleSummary.textContent = "No schedule insights are available because no tasks were scheduled.";
      }
      if (conflictOutput) {
        conflictOutput.innerHTML = "<p>No conflicts detected.</p>";
      }

      return;
    }

    renderSchedule(scheduleData);
    updateScheduleLoad(scheduleData);
    generateScheduleSummary(scheduleData);

    const conflicts = detectAllScheduleConflicts(scheduleData);
    renderConflictAlerts(conflicts);
  } catch (err) {
    console.error(err);
    scheduleOutput.innerHTML = "<p>No scheduled tasks available.</p>";

    if (scheduleMessage) {
      scheduleMessage.textContent = "Failed to refresh schedule.";
      scheduleMessage.className = "message error";
    }
  }
}


/** Feature -- Will Keep  */


function loadSavedScheduleSettings() {
  const savedRange = localStorage.getItem("momentumScheduleRange");
  const savedMaxTasks = localStorage.getItem("momentumMaxTasksPerDay");

  if (savedRange && scheduleRange) {
    scheduleRange.value = savedRange;
  }

  if (savedMaxTasks && maxTasksPerDay) {
    maxTasksPerDay.value = savedMaxTasks;
  }
}

async function handleGenerateSchedule() {
  if (!scheduleMessage || !scheduleOutput) return;

  scheduleMessage.textContent = "";
  scheduleMessage.className = "message";

  const days = scheduleRange ? Number(scheduleRange.value) : 7;
  const max_tasks_per_day = maxTasksPerDay ? Number(maxTasksPerDay.value) : 4;

  try {
    const res = await fetch("/api/schedule", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ days, max_tasks_per_day })
    });

    const data = await res.json();

    if (!res.ok) {
      scheduleMessage.textContent = data.error || "Failed to generate schedule.";
      scheduleMessage.className = "message error";

      if (scheduleLoadFill) scheduleLoadFill.style.width = "0%";
      if (scheduleLoadPercent) scheduleLoadPercent.textContent = "0%";
      if (scheduleLoadText) scheduleLoadText.textContent = "0 / 0 slots used";
      if (scheduleSummary) {
        scheduleSummary.textContent = "Unable to generate schedule insights right now.";
      }

      return;
    }

    scheduleMessage.textContent = data.message || "Schedule generated successfully.";
    scheduleMessage.className = "message success";

    const scheduleData = data.schedule || {};

    renderSchedule(scheduleData);
    updateScheduleLoad(scheduleData);
    generateScheduleSummary(scheduleData);
    
    localStorage.setItem("momentumScheduleRange", String(days));
localStorage.setItem("momentumMaxTasksPerDay", String(max_tasks_per_day));
localStorage.setItem("momentumScheduleGenerated", "true");
  } catch (err) {
    console.error(err);

    scheduleMessage.textContent = "Failed to generate schedule.";
    scheduleMessage.className = "message error";

    if (scheduleLoadFill) scheduleLoadFill.style.width = "0%";
    if (scheduleLoadPercent) scheduleLoadPercent.textContent = "0%";
    if (scheduleLoadText) scheduleLoadText.textContent = "0 / 0 slots used";
    if (scheduleSummary) {
      scheduleSummary.textContent = "Unable to generate schedule insights right now.";
    }
  }
}

if (generateScheduleBtn) {
  generateScheduleBtn.addEventListener("click", handleGenerateSchedule);
}

// ---------- Dashboard Constants ----------
const totalTasksEl = document.getElementById("totalTasks");
const pendingTasksEl = document.getElementById("pendingTasks");
const completedTasksEl = document.getElementById("completedTasks");
const recentTasksBody = document.getElementById("recentTasksBody");
const progressFill = document.getElementById("progressFill");
const progressPercent = document.getElementById("progressPercent");
const progressText = document.getElementById("progressText");



/* Feature When We Load DashBoard */

async function loadDashboard() {
  if (!totalTasksEl || !pendingTasksEl || !completedTasksEl || !recentTasksBody) return;

  try {
    const res = await fetch("/api/tasks?sort=date");
    const tasks = await res.json();

    if (!res.ok) {
      throw new Error(tasks.error || "Failed to load dashboard data.");
    }

    const totalTasks = tasks.length;
    const pendingCount = tasks.filter(t => t.status !== "Completed").length;
    const completedCount = tasks.filter(t => t.status === "Completed").length;

    totalTasksEl.textContent = totalTasks;
    pendingTasksEl.textContent = pendingCount;
    completedTasksEl.textContent = completedCount;

    const completionPercent = totalTasks > 0
      ? Math.round((completedCount / totalTasks) * 100)
      : 0;

    if (progressFill) {
      progressFill.style.width = `${completionPercent}%`;
    }

    if (progressPercent) {
      progressPercent.textContent = `${completionPercent}%`;
    }

    if (progressText) {
      progressText.textContent = `${completedCount} / ${totalTasks} tasks completed`;
    }

    recentTasksBody.innerHTML = "";

    if (!tasks.length) {
      recentTasksBody.innerHTML = `
        <tr>
          <td colspan="4">No tasks available.</td>
        </tr>
      `;
      return;
    }

    const recentTasks = tasks.slice(0, 5);

    recentTasks.forEach((task) => {
      let statusClass = "status-pending";
      if (task.status === "In Progress") statusClass = "status-progress";
      if (task.status === "Completed") statusClass = "status-completed";

      let priorityClass = "priority-low";
      if (task.priority === "High") priorityClass = "priority-high";
      if (task.priority === "Medium") priorityClass = "priority-medium";

      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${task.title}</td>
        <td><span class="status-badge ${statusClass}">${task.status}</span></td>
        <td>${task.due_date}</td>
        <td><span class="priority-pill ${priorityClass}">${task.priority}</span></td>
      `;
      recentTasksBody.appendChild(row);
    });
  } catch (err) {
    console.error(err);

    if (recentTasksBody) {
      recentTasksBody.innerHTML = `
        <tr>
          <td colspan="4">Failed to load dashboard data.</td>
        </tr>
      `;
    }

    if (progressFill) {
      progressFill.style.width = "0%";
    }

    if (progressPercent) {
      progressPercent.textContent = "0%";
    }

    if (progressText) {
      progressText.textContent = "Unable to load progress";
    }
  }
}

/** Feature: Helper Method for Time Conversion */



function parseTimeToMinutes(timeStr) {
  const [timePart, meridiem] = timeStr.split(" ");
  let [hours, minutes] = timePart.split(":").map(Number);

  if (meridiem === "PM" && hours !== 12) hours += 12;
  if (meridiem === "AM" && hours === 12) hours = 0;

  return hours * 60 + minutes;
}

function findScheduleConflicts(tasksForDay) {
  const conflicts = [];

  for (let i = 0; i < tasksForDay.length; i++) {
    const current = tasksForDay[i];
    const currentStart = parseTimeToMinutes(current.scheduled_start);
    const currentEnd = parseTimeToMinutes(current.scheduled_end);

    for (let j = i + 1; j < tasksForDay.length; j++) {
      const next = tasksForDay[j];
      const nextStart = parseTimeToMinutes(next.scheduled_start);
      const nextEnd = parseTimeToMinutes(next.scheduled_end);

      const overlaps = currentStart < nextEnd && nextStart < currentEnd;

      if (overlaps) {
        conflicts.push({
          firstTaskId: current.id,
          secondTaskId: next.id,
          firstTask: current,
          secondTask: next
        });
      }
    }
  }

  return conflicts;
}

function parseTimeToMinutes(timeStr) {
  const [timePart, meridiem] = timeStr.split(" ");
  let [hours, minutes] = timePart.split(":").map(Number);

  if (meridiem === "PM" && hours !== 12) hours += 12;
  if (meridiem === "AM" && hours === 12) hours = 0;

  return hours * 60 + minutes;
}


/** User Story #7: Conflict Detection  */

function findScheduleConflicts(tasksForDay) {
  const conflicts = [];

  for (let i = 0; i < tasksForDay.length; i++) {
    const firstTask = tasksForDay[i];
    const firstStart = parseTimeToMinutes(firstTask.scheduled_start);
    const firstEnd = parseTimeToMinutes(firstTask.scheduled_end);

    for (let j = i + 1; j < tasksForDay.length; j++) {
      const secondTask = tasksForDay[j];
      const secondStart = parseTimeToMinutes(secondTask.scheduled_start);
      const secondEnd = parseTimeToMinutes(secondTask.scheduled_end);

      const overlaps = firstStart < secondEnd && secondStart < firstEnd;

      if (overlaps) {
        conflicts.push({
          firstTaskId: firstTask.id,
          secondTaskId: secondTask.id,
          firstTask,
          secondTask
        });
      }
    }
  }

  return conflicts;
}





function loadSavedSchedule() {
  if (!scheduleOutput) return;

  const savedSchedule = localStorage.getItem("momentumSchedule");
  const savedRange = localStorage.getItem("momentumScheduleRange");
  const savedMaxTasks = localStorage.getItem("momentumMaxTasksPerDay");

  if (savedRange && scheduleRange) {
    scheduleRange.value = savedRange;
  }

  if (savedMaxTasks && maxTasksPerDay) {
    maxTasksPerDay.value = savedMaxTasks;
  }

  if (!savedSchedule) {
    scheduleOutput.innerHTML = "<p>No scheduled tasks available.</p>";
    return;
  }

  const scheduleData = JSON.parse(savedSchedule);

  renderSchedule(scheduleData);
  updateScheduleLoad(scheduleData);
  generateScheduleSummary(scheduleData);

  const conflicts = detectAllScheduleConflicts(scheduleData);
  renderConflictAlerts(conflicts);
}


//** Feature for UI : No Functionality with Actual Code  */


function initMomentumOrb() {
  const orbWrap = document.querySelector(".hero-orb-wrap") || document.getElementById("momentumOrbWrap");
  const orbCanvas = document.getElementById("momentumOrbCanvas");

  console.log("initMomentumOrb running");
  console.log("orbWrap:", orbWrap);
  console.log("orbCanvas:", orbCanvas);
  console.log("THREE:", typeof THREE);

  if (!orbWrap || !orbCanvas || typeof THREE === "undefined") return;

  const scene = new THREE.Scene();

  const camera = new THREE.PerspectiveCamera(
    45,
    orbWrap.clientWidth / orbWrap.clientHeight,
    0.1,
    1000
  );
  camera.position.set(0, 0, 6);

  const renderer = new THREE.WebGLRenderer({
    canvas: orbCanvas,
    antialias: true,
    alpha: true
  });

  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(orbWrap.clientWidth, orbWrap.clientHeight);

  // Main orb
  const sphereGeometry = new THREE.SphereGeometry(1.55, 64, 64);
  const sphereMaterial = new THREE.MeshStandardMaterial({
    color: 0x7c3aed,
    emissive: 0x4c1d95,
    emissiveIntensity: 0.9,
    roughness: 0.28,
    metalness: 0.22
  });
  const orb = new THREE.Mesh(sphereGeometry, sphereMaterial);
  scene.add(orb);

  // Glow shell
  const glowGeometry = new THREE.SphereGeometry(1.82, 64, 64);
  const glowMaterial = new THREE.MeshBasicMaterial({
    color: 0xc084fc,
    transparent: true,
    opacity: 0.12
  });
  const glow = new THREE.Mesh(glowGeometry, glowMaterial);
  scene.add(glow);

  // Ring
  const ringGeometry = new THREE.TorusGeometry(2.15, 0.03, 16, 160);
  const ringMaterial = new THREE.MeshBasicMaterial({
    color: 0xd8b4fe,
    transparent: true,
    opacity: 0.65
  });
  const ring = new THREE.Mesh(ringGeometry, ringMaterial);
  ring.rotation.x = 1.1;
  ring.rotation.y = 0.35;
  scene.add(ring);

  // Floating particles
  const particleGroup = new THREE.Group();
  const particleMaterial = new THREE.MeshBasicMaterial({ color: 0xf5d0fe });

  for (let i = 0; i < 14; i++) {
    const particle = new THREE.Mesh(
      new THREE.SphereGeometry(0.045, 10, 10),
      particleMaterial
    );

    const angle = (i / 14) * Math.PI * 2;
    const radius = 2.45 + Math.random() * 0.22;
    const y = (Math.random() - 0.5) * 1.8;

    particle.position.set(
      Math.cos(angle) * radius,
      y,
      Math.sin(angle) * radius
    );

    particleGroup.add(particle);
  }

  scene.add(particleGroup);

  // Lighting
  const ambientLight = new THREE.AmbientLight(0xffffff, 1.4);
  scene.add(ambientLight);

  const pointLight = new THREE.PointLight(0xc084fc, 2.2, 20);
  pointLight.position.set(4, 3, 5);
  scene.add(pointLight);

  const backLight = new THREE.PointLight(0x60a5fa, 1.2, 18);
  backLight.position.set(-4, -2, -4);
  scene.add(backLight);

  const clock = new THREE.Clock();

  // Drag controls
  let isDragging = false;
  let previousMouseX = 0;
  let previousMouseY = 0;

  let targetRotationY = 0;
  let targetRotationX = 0;

  let currentRotationY = 0;
  let currentRotationX = 0;

  orbCanvas.addEventListener("mousedown", (e) => {
    isDragging = true;
    previousMouseX = e.clientX;
    previousMouseY = e.clientY;
    orbCanvas.classList.add("dragging");
  });

  window.addEventListener("mouseup", () => {
    isDragging = false;
    orbCanvas.classList.remove("dragging");
  });

  window.addEventListener("mousemove", (e) => {
    if (!isDragging) return;

    const deltaX = e.clientX - previousMouseX;
    const deltaY = e.clientY - previousMouseY;

    targetRotationY += deltaX * 0.008;
    targetRotationX += deltaY * 0.004;

    targetRotationX = Math.max(-0.6, Math.min(0.6, targetRotationX));

    previousMouseX = e.clientX;
    previousMouseY = e.clientY;
  });

  // Touch support
  orbCanvas.addEventListener("touchstart", (e) => {
    if (!e.touches.length) return;
    isDragging = true;
    previousMouseX = e.touches[0].clientX;
    previousMouseY = e.touches[0].clientY;
  }, { passive: true });

  window.addEventListener("touchend", () => {
    isDragging = false;
  });

  window.addEventListener("touchmove", (e) => {
    if (!isDragging || !e.touches.length) return;

    const deltaX = e.touches[0].clientX - previousMouseX;
    const deltaY = e.touches[0].clientY - previousMouseY;

    targetRotationY += deltaX * 0.008;
    targetRotationX += deltaY * 0.004;

    targetRotationX = Math.max(-0.6, Math.min(0.6, targetRotationX));

    previousMouseX = e.touches[0].clientX;
    previousMouseY = e.touches[0].clientY;
  }, { passive: true });

  function animate() {
    requestAnimationFrame(animate);

    const elapsed = clock.getElapsedTime();

    // Idle auto-spin when not dragging
    if (!isDragging) {
      targetRotationY += 0.003;
    }

    // Smooth interpolation
    currentRotationY += (targetRotationY - currentRotationY) * 0.08;
    currentRotationX += (targetRotationX - currentRotationX) * 0.08;

    orb.rotation.y = currentRotationY;
    orb.rotation.x = currentRotationX + Math.sin(elapsed * 0.6) * 0.04;

    glow.rotation.y = currentRotationY * 0.92;
    glow.rotation.x = currentRotationX * 0.92;
    glow.scale.setScalar(1 + Math.sin(elapsed * 1.5) * 0.012);

    ring.rotation.z += 0.0025;
    particleGroup.rotation.y += 0.002;
    particleGroup.rotation.x = Math.sin(elapsed * 0.35) * 0.08;

    renderer.render(scene, camera);
  }

  function handleResize() {
    const width = orbWrap.clientWidth;
    const height = orbWrap.clientHeight;

    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
  }

  window.addEventListener("resize", handleResize);

  animate();
 

}

function detectAllScheduleConflicts(schedule) {
  const allConflicts = [];

  Object.entries(schedule).forEach(([dayKey, tasksForDay]) => {
    const dayConflicts = findScheduleConflicts(tasksForDay).map(conflict => ({
      dayKey,
      ...conflict
    }));

    allConflicts.push(...dayConflicts);
  });

  return allConflicts;
}




const conflictOutput = document.getElementById("conflictOutput");

function renderConflictAlerts(conflicts) {
  if (!conflictOutput) return;

  if (!conflicts.length) {
    conflictOutput.innerHTML = `<p>No conflicts detected.</p>`;
    return;
  }

  conflictOutput.innerHTML = `
    <div class="message error">
      Schedule conflict detected.
    </div>
  `;

  conflicts.forEach(conflict => {
    const item = document.createElement("div");
    item.className = "conflict-item";
    item.innerHTML = `
      <p>
        <strong>${conflict.firstTask.title}</strong>
        (${conflict.firstTask.scheduled_start} – ${conflict.firstTask.scheduled_end})
        overlaps with
        <strong>${conflict.secondTask.title}</strong>
        (${conflict.secondTask.scheduled_start} – ${conflict.secondTask.scheduled_end})
        on ${conflict.dayKey}.
      </p>
      <p class="due-meta">Suggested next slot: after ${conflict.firstTask.scheduled_end}</p>
    `;
    conflictOutput.appendChild(item);
  });
}


function closeIntroOverlay() {
  if (!introOverlay) return;
  introOverlay.classList.add("fade-out");

  setTimeout(() => {
    introOverlay.remove();
  }, 900);
}

if (introContinueBtn) {
  introContinueBtn.addEventListener("click", closeIntroOverlay);
}

if (introOverlay) {
  setTimeout(() => {
    if (document.body.contains(introOverlay)) {
      closeIntroOverlay();
    }
  }, 5000);
}



// ---------- Initial load ----------
if (tbody && sortSelect) {
  fetchTasks();
}

loadDashboard();
loadQuote();

const orbCanvas = document.getElementById("momentumOrbCanvas");
if (orbCanvas) {
  initMomentumOrb();
}

if (scheduleOutput) {
  loadSavedScheduleSettings();
  refreshScheduleView();
}



/*
const DEBUG_CONFLICT_TEST = true;

if (DEBUG_CONFLICT_TEST && scheduleOutput) {
  const todayKey = formatLocalDateKey(new Date());

  const testConflictSchedule = {
    [todayKey]: [
      {
        id: 1,
        title: "Task A",
        status: "Pending",
        due_date: `${todayKey} 15:00`,
        priority: "High",
        effort_level: "Medium",
        category: "School",
        scheduled_start: "2:00 PM",
        scheduled_end: "3:00 PM"
      },
      {
        id: 2,
        title: "Task B",
        status: "Pending",
        due_date: `${todayKey} 16:00`,
        priority: "Medium",
        effort_level: "High",
        category: "Work",
        scheduled_start: "2:30 PM",
        scheduled_end: "3:30 PM"
      }
    ]
  };

  renderSchedule(testConflictSchedule);

  const conflicts = detectAllScheduleConflicts(testConflictSchedule);
  console.log("TEST CONFLICTS:", conflicts);

  renderConflictAlerts(conflicts);
}
*/