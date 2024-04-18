window.addEventListener('load', function () {
    const tdElements = document?.querySelectorAll('.timestamps')

    tdElements.forEach(td => {
        const rawTimestamp = td.textContent.trim() // Get raw timestamp

        const date = new Date(rawTimestamp)

        const options = {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: 'numeric',
            minute: 'numeric',
            hour12: true, // For 12-hour AM/PM format
        }

        const formattedDateTime = date.toLocaleString('en-US', options)

        td.textContent = formattedDateTime
    })

    const inputFile = document?.getElementById('dropzone-file')
    const fileNameDisplay = document?.getElementById('selected-file-display')

    inputFile.addEventListener('change', event => {
        const selectedFile = event.target.files[0]

        if (selectedFile) {
            document
                ?.getElementById('upload-file-button')
                .classList.remove('hidden')
            document
                ?.getElementById('upload-details-minor')
                .classList.add('hidden')

            const filename = selectedFile.name

            const p = document.createElement('p')
            p.className =
                'text-xs text-center text-gray-500 dark:text-gray-400 uppercase tracking-wider font-semibold'
            p.textContent = filename

            fileNameDisplay.appendChild(p)
        }
    })
})
