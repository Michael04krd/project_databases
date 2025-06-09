const API_BASE_URL = 'http://127.0.0.1:8000'
const API_TOKEN = localStorage.getItem('access_token')
let currentPage = 1
let workersPerPage = 10
let totalWorkers = 0
let workersData = []
let workerToDelete = null

document.addEventListener('DOMContentLoaded', function () {
	loadMedicalWorkers()

	document.getElementById('saveMedicalWorkerBtn').addEventListener('click', addMedicalWorker)
	document.getElementById('updateMedicalWorkerBtn').addEventListener('click', updateMedicalWorker)
	document.getElementById('confirmDeleteBtn').addEventListener('click', deleteMedicalWorker)
})

async function loadMedicalWorkers(page = 1) {
	try {
		const response = await fetch(`${API_BASE_URL}/admin/med_workers`, {
			method: 'GET',
			headers: {
				Authorization: `Bearer ${API_TOKEN}`,
				'Content-Type': 'application/json',
			},
		})

		if (!response.ok) {
			const errorData = await response.json()
			throw new Error(errorData.detail || 'Ошибка при загрузке данных')
		}

		const data = await response.json()

		workersData = data.map(worker => ({
			id: worker.id,
			user_id: worker.user_id,
			surname: worker.user.surname,
			name: worker.user.name,
			namedad: worker.user.namedad,
			email: worker.user.email,
			position: worker.job_title,
			hospital: worker.hospital,
			phone: worker.phone,
			is_active: worker.user.is_active,
		}))

		totalWorkers = workersData.length
		updateStatistics(workersData)
		renderWorkersTable(workersData)
		renderPagination()
	} catch (error) {
		console.error('Ошибка:', error)
		alert('Произошла ошибка при загрузке данных: ' + error.message)
	}
}

function updateStatistics(data) {
	const total = data.length
	const active = data.filter(worker => worker.is_active).length
	const inactive = total - active

	document.getElementById('totalWorkersCount').textContent = total
	document.getElementById('activeWorkersCount').textContent = active
	document.getElementById('inactiveWorkersCount').textContent = inactive
}

function renderWorkersTable(data) {
	const tableBody = document.getElementById('workersTableBody')
	tableBody.innerHTML = ''

	const startIndex = (currentPage - 1) * workersPerPage
	const endIndex = Math.min(startIndex + workersPerPage, data.length)

	for (let i = startIndex; i < endIndex; i++) {
		const worker = data[i]
		const row = document.createElement('tr')

		row.innerHTML = `
                    <td>${worker.id}</td>
                    <td>${worker.surname} ${worker.name} ${worker.namedad || ''}</td>
                    <td>${worker.position}</td>
                    <td>${worker.hospital}</td>
                    <td>${worker.phone}</td>
                    <td><span class="badge ${worker.is_active ? 'bg-success' : 'bg-warning'}">${
			worker.is_active ? 'Активен' : 'Неактивен'
		}</span></td>
                    <td>
                        <button class="btn btn-sm btn-primary action-btn edit-btn" data-id="${worker.id}">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-sm btn-danger action-btn delete-btn" data-id="${worker.id}">
                            <i class="bi bi-trash"></i>
                        </button>
                    </td>
                `

		tableBody.appendChild(row)
	}

	document.querySelectorAll('.edit-btn').forEach(btn => {
		btn.addEventListener('click', function () {
			const workerId = this.getAttribute('data-id')
			openEditModal(workerId)
		})
	})

	document.querySelectorAll('.delete-btn').forEach(btn => {
		btn.addEventListener('click', function () {
			const workerId = this.getAttribute('data-id')
			openDeleteModal(workerId)
		})
	})
}

function renderPagination() {
	const pagination = document.getElementById('pagination')
	pagination.innerHTML = ''

	const totalPages = Math.ceil(totalWorkers / workersPerPage)

	const prevLi = document.createElement('li')
	prevLi.className = `page-item ${currentPage === 1 ? 'disabled' : ''}`
	prevLi.innerHTML = `<a class="page-link" href="#" tabindex="-1" aria-disabled="true">Назад</a>`
	prevLi.addEventListener('click', function (e) {
		e.preventDefault()
		if (currentPage > 1) {
			currentPage--
			renderWorkersTable(workersData)
			renderPagination()
		}
	})
	pagination.appendChild(prevLi)

	for (let i = 1; i <= totalPages; i++) {
		const pageLi = document.createElement('li')
		pageLi.className = `page-item ${i === currentPage ? 'active' : ''}`
		pageLi.innerHTML = `<a class="page-link" href="#">${i}</a>`
		pageLi.addEventListener('click', function (e) {
			e.preventDefault()
			currentPage = i
			renderWorkersTable(workersData)
			renderPagination()
		})
		pagination.appendChild(pageLi)
	}

	const nextLi = document.createElement('li')
	nextLi.className = `page-item ${currentPage === totalPages ? 'disabled' : ''}`
	nextLi.innerHTML = `<a class="page-link" href="#">Вперед</a>`
	nextLi.addEventListener('click', function (e) {
		e.preventDefault()
		if (currentPage < totalPages) {
			currentPage++
			renderWorkersTable(workersData)
			renderPagination()
		}
	})
	pagination.appendChild(nextLi)
}

function openAddModal() {
	document.getElementById('addMedicalWorkerForm').reset()
}

function openEditModal(workerId) {
	const worker = workersData.find(w => w.id == workerId)
	if (!worker) return

	document.getElementById('editWorkerId').value = worker.id
	document.getElementById('editSurname').value = worker.surname
	document.getElementById('editName').value = worker.name
	document.getElementById('editNamedad').value = worker.namedad || ''
	document.getElementById('editEmail').value = worker.email
	document.getElementById('editJobTitle').value = worker.position
	document.getElementById('editHospital').value = worker.hospital
	document.getElementById('editPhone').value = worker.phone
	document.getElementById('editStatus').value = worker.is_active ? 'active' : 'inactive'

	const modal = new bootstrap.Modal(document.getElementById('editMedicalWorkerModal'))
	modal.show()
}

function openDeleteModal(workerId) {
	workerToDelete = workerId
	const modal = new bootstrap.Modal(document.getElementById('deleteConfirmationModal'))
	modal.show()
}

async function addMedicalWorker() {
	const formData = {
		email: document.getElementById('email').value,
		password: document.getElementById('password').value,
		surname: document.getElementById('surname').value,
		name: document.getElementById('name').value,
		namedad: document.getElementById('namedad').value || null,
		job_title: document.getElementById('jobTitle').value,
		hospital: document.getElementById('hospital').value,
		phone: document.getElementById('phone').value.replace(/\D/g, ''),
	}

	try {
		const response = await fetch(`${API_BASE_URL}/admin/create_med_workers`, {
			method: 'POST',
			headers: {
				Authorization: `Bearer ${API_TOKEN}`,
				'Content-Type': 'application/json',
			},
			body: JSON.stringify(formData),
		})

		if (!response.ok) {
			const errorData = await response.json()
			console.error('Server error details:', errorData)
			throw new Error(errorData.detail || 'Ошибка сервера')
		}

		const result = await response.json()
		console.log('Success:', result)

		const modal = bootstrap.Modal.getInstance(document.getElementById('addMedicalWorkerModal'))
		modal.hide()
		loadMedicalWorkers()
		alert('Медработник успешно создан!')
	} catch (error) {
		console.error('Error:', error)
		alert(`Ошибка: ${error.message}`)
	}
}

async function updateMedicalWorker() {
	const workerId = document.getElementById('editWorkerId').value
	const formData = {
		surname: document.getElementById('editSurname').value,
		name: document.getElementById('editName').value,
		namedad: document.getElementById('editNamedad').value,
		email: document.getElementById('editEmail').value,
		password: document.getElementById('editPassword').value || undefined,
		job_title: document.getElementById('editJobTitle').value,
		hospital: document.getElementById('editHospital').value,
		phone: document.getElementById('editPhone').value,
		is_active: document.getElementById('editStatus').value === 'active',
	}

	try {
		const response = await fetch(`${API_BASE_URL}/admin/med_workers/${workerId}`, {
			method: 'PUT',
			headers: {
				Authorization: `Bearer ${API_TOKEN}`,
				'Content-Type': 'application/json',
			},
			body: JSON.stringify(formData),
		})

		if (!response.ok) {
			const errorData = await response.json()
			throw new Error(errorData.detail || 'Ошибка при обновлении')
		}

		const data = await response.json()

		const modal = bootstrap.Modal.getInstance(document.getElementById('editMedicalWorkerModal'))
		modal.hide()

		loadMedicalWorkers()

		alert('Данные успешно обновлены!')
	} catch (error) {
		console.error('Ошибка:', error)
		alert('Произошла ошибка: ' + error.message)
	}
}

function openDeleteModal(workerId) {
	workerToDelete = workerId
	const modal = new bootstrap.Modal(document.getElementById('deleteConfirmationModal'))
	modal.show()
}

async function deleteMedicalWorker() {
	if (!workerToDelete) return

	try {
		const response = await fetch(`${API_BASE_URL}/admin/med_workers/${workerToDelete}`, {
			method: 'DELETE',
			headers: {
				Authorization: `Bearer ${API_TOKEN}`,
				'Content-Type': 'application/json',
			},
		})

		if (!response.ok) {
			const errorData = await response.json()
			throw new Error(errorData.detail || 'Ошибка при удалении')
		}

		const modal = bootstrap.Modal.getInstance(document.getElementById('deleteConfirmationModal'))
		modal.hide()

		loadMedicalWorkers()
		alert('Медработник успешно удалён')
	} catch (error) {
		alert(error.message)
	} finally {
		workerToDelete = null
	}
}
