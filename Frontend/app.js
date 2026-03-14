const form = document.getElementById("taskForm");
const msg = document.getElementById("message");
const tbody = document.getElementById("taskTableBody");
const sortSelect = document.getElementById("sortSelect");

//This is what Connects to Our HTML( Edit, Schedule,etc..) -- All the functions in this JS file, the functions in this file.
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
const scheduleLoadFill = document.getElementById("scheduleLoadFill");
const scheduleLoadPercent = document.getElementById("scheduleLoadPercent");
const scheduleLoadText = document.getElementById("scheduleLoadText");
const scheduleSummary = document.getElementById("scheduleSummary");
const introOverlay = document.getElementById("introOverlay");
const introContinueBtn = document.getElementById("introContinueBtn");

// Store original task values so we can compare after edit
let originalTaskData = null;

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



/*
========================================================
User Story #59 – Overdue Task Highlighting

As a user, I want overdue tasks to be visually highlighted
so that I can easily identify tasks that require immediate attention.

Implementation:
This logic checks task due dates when rendering tasks.
If a task's due date is earlier than the current date and
the task is not completed, a visual highlight is applied
to the task row.

UI Result:
Overdue tasks appear visually distinct in the Task Log.
========================================================
*/




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

/* 

Purpose

Handles temporary success and error messages shown to the user after actions such as creating or editing tasks. Messages automatically disappear after a short delay to keep the interface clean.

⸻

Function: clearCreateMessageAfterDelay()

Purpose

Automatically clears the task creation message after a specified amount of time.

How It Works
	•	Uses setTimeout() to wait a specified number of milliseconds.
	•	After the delay:
	•	The message text is cleared.
	•	The message styling is reset to the default "message" class.


Function: clearEditMessageAfterDelay()

Purpose

Automatically clears the task editing message after a short delay.

How It Works
	•	Uses setTimeout() to wait 5 seconds.
	•	Clears the edit message text and resets the message styling.

Example Use Case


*/ 

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

// ---------- Fetch + Render ----------
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
========================================================
Feature: AI Schedule Insights / Schedule Summary

Purpose:
This function analyzes the generated schedule and produces a short,
human-readable summary explaining scheduling decisions.

What it evaluates:
- Total number of scheduled tasks
- Number of days used in the schedule
- Number of high priority tasks
- Number of high effort tasks
- Busiest day workload

Based on these metrics, the system generates insights such as:
- prioritizing urgent tasks
- scheduling high effort tasks earlier
- spreading workload across days
- identifying heavy workload days

Result:
A short summary is displayed in the UI to help the user understand
their generated schedule.
========================================================
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



/*
========================================================
Feature: Task Completion System

User Story:


Description:
This function updates a task's status to "Completed" by sending
a PUT request to the backend API. After completion:

1. The task is updated in the database.
2. The task list refreshes to reflect the new status.
3. Dashboard statistics are updated.
4. A success message appears with an option to undo the action.

If the user clicks "Undo", the system restores the task to its
previous status.
========================================================
*/




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


/*
========================================================
Feature: Visual Task Update Highlighting

User Story:
As a user, I want to clearly see what fields changed after
editing a task so that I can quickly identify the updates
that were applied.

Description:
This function compares the updated task values with the
original task data and visually highlights any fields that
were modified.

How it works:
1. Finds the task row in the Task Log using the task ID.
2. Compares each updated field with the original task values.
3. If a value changed, the corresponding table cell receives
   the CSS class "updated-field".
4. The entire row temporarily receives the class "updated-row"
   to draw attention to the update.
5. After 2.5 seconds, all highlight styling is automatically
   removed.

Fields Checked:
- Title
- Status
- Due date
- Priority
- Duration
- Effort level
- Start restriction
- Category

Result:
Users receive immediate visual feedback showing which
task information was changed.
========================================================
*/


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

// ---------- Create Task ----------
if (form) {
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    msg.textContent = "";
    msg.className = "message";

    const title = document.getElementById("title").value.trim();
    const dueInput = document.getElementById("dueDate").value.trim();
    const priority = document.getElementById("priority").value;
    const durationMinutes = document.getElementById("durationMinutes").value;
    const effortLevel = document.getElementById("effortLevel").value;
    const startAfterInput = document.getElementById("startAfter").value.trim();
    const category = document.getElementById("category").value;
    const dueDateMsg = document.getElementById("dueDateMsg");

    dueDateMsg.textContent = "";

    if (!validateFutureDate(dueInput, dueDateMsg)) {
      return;
    }

    const due_date = formatForBackend(dueInput);
    const start_after = startAfterInput ? formatForBackend(startAfterInput) : null;

    if (!title || !due_date) {
      msg.textContent = "Title and due date are required.";
      msg.className = "message error";
      return;
    }

    try {
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
        msg.textContent = data.error || "Failed to create task.";
        msg.className = "message error";
        return;
      }

      form.reset();
      dueDateMsg.textContent = "";
      msg.textContent = "✓ Task created successfully!";
      msg.className = "message success";

      //Acceptance Critera #1: Auto efresh

      await fetchTasks();
      await refreshScheduleView();
      clearCreateMessageAfterDelay();
    } catch (err) {
      msg.textContent = "Failed to create task.";
      msg.className = "message error";
      console.error(err);
    }
  });
}





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

/*
========================================================
Feature: Edit Task

User Story:
As a user, I want to edit existing tasks so that
I can update task information when plans change.

Description:
This event listener handles submission of the
task editing form.

Workflow:
1. Prevents default form submission.
2. Collects updated task values from the form.
3. Validates required fields and due date.
4. Sends a PUT request to update the task.
5. Refreshes the task list.
6. Highlights the fields that were updated.

Result:
The user receives immediate visual feedback
showing which fields changed.
========================================================
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

function closeEditForm() {
  editSection.style.display = "none";
  editForm.reset();
  editTaskId.value = "";
  editMessage.textContent = "";
  editMessage.className = "message";
  editDueDateMsg.textContent = "";
  originalTaskData = null;
}


/*
========================================================
Feature: Delete Task

User Story:
As a user, I want to delete tasks I no longer need
so that my task list stays clean and relevant.

Description:
This function handles task deletion when the user clicks
the "Delete" button in the Task Log.

How it works:
1. Prompts the user with a confirmation dialog.
2. Sends a DELETE request to the backend API.
3. If successful, refreshes the task list.
4. Displays a temporary success or error message.

Safety:
A confirmation popup prevents accidental deletion.
========================================================
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

// ---------- Schedule Generation Variables ----------
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

  scheduleOutput.innerHTML = '<div class="schedule-grid"></div>';
  const grid = scheduleOutput.querySelector(".schedule-grid");

  let hasAnyTasks = false;

  for (let i = 0; i < selectedDays; i++) {
    const currentDate = new Date();
    currentDate.setDate(today.getDate() + i);

    const dayKey = formatLocalDateKey(currentDate);
    const tasksForDay = schedule[dayKey] || [];

    const dayCard = document.createElement("div");
    dayCard.className = "schedule-day";

    if (dayKey === todayString) {
      dayCard.classList.add("today");
    }

    const heading = document.createElement("h3");
    heading.innerHTML = `
      ${currentDate.toLocaleDateString(undefined, { weekday: "long" })}
      <span class="schedule-day-date">
        ${currentDate.toLocaleDateString(undefined, {
          month: "short",
          day: "numeric",
          year: "numeric"
        })}
      </span>
    `;
    dayCard.appendChild(heading);

    if (!tasksForDay.length) {
      const emptyText = document.createElement("p");
      emptyText.className = "schedule-empty";
      emptyText.textContent = "No tasks scheduled.";
      dayCard.appendChild(emptyText);
      grid.appendChild(dayCard);
      continue;
    }

    hasAnyTasks = true;

    tasksForDay.forEach((task) => {
      let statusClass = "status-pending";
      if (task.status === "In Progress") statusClass = "status-progress";
      if (task.status === "Completed") statusClass = "status-completed";

      let priorityClass = "priority-low";
      if (task.priority === "High") priorityClass = "priority-high";
      if (task.priority === "Medium") priorityClass = "priority-medium";

      const taskCard = document.createElement("div");
      taskCard.className = "schedule-task";

      if (conflictingTaskIds.has(task.id)) {
        taskCard.classList.add("conflict-task");
      }

      taskCard.innerHTML = `
        ${conflictingTaskIds.has(task.id) ? '<div class="conflict-label">CONFLICT</div>' : ""}
        <div class="calendar-task-time">${task.scheduled_start} – ${task.scheduled_end}</div>
        <div class="calendar-task-title">${task.title}</div>
        <div class="calendar-task-meta">
          <span class="status-badge ${statusClass}">${task.status}</span>
          <span class="priority-pill ${priorityClass}">${task.priority} Priority</span>
          <span class="task-meta-pill">${task.effort_level} Effort</span>
          <span class="task-meta-pill">${task.category}</span>
        </div>
        <div class="due-meta" style="margin-top:10px;">
          Due: ${task.due_date}
        </div>
      `;

      dayCard.appendChild(taskCard);
    });

    grid.appendChild(dayCard);
  }

  if (!hasAnyTasks) {
    scheduleMessage.textContent = "No tasks available to schedule.";
    scheduleMessage.className = "message error";
  }
}

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

async function refreshScheduleView() {
  if (!scheduleOutput) return;

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

// ---------- Dashboard ----------
const totalTasksEl = document.getElementById("totalTasks");
const pendingTasksEl = document.getElementById("pendingTasks");
const completedTasksEl = document.getElementById("completedTasks");
const recentTasksBody = document.getElementById("recentTasksBody");
const progressFill = document.getElementById("progressFill");
const progressPercent = document.getElementById("progressPercent");
const progressText = document.getElementById("progressText");

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


/* 
User Story -- Conflict Detection Use

*/



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