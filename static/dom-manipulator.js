window.addEventListener('load', function () {
    var tdElements = document?.querySelectorAll('.timestamps')
    tdElements.forEach(td => {
        var rawTimestamp = td.textContent.trim()
        var date = new Date(rawTimestamp)
        var options = {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: 'numeric',
            minute: 'numeric',
            hour12: true,
        }
        td.textContent = date.toLocaleString('en-US', options)
    })

    const humanizeFileSize = size => {
        const i = size === 0 ? 0 : Math.floor(Math.log(size) / Math.log(1024))
        return (
            (size / Math.pow(1024, i)).toFixed(2) * 1 +
            ' ' +
            ['B', 'kB', 'MB', 'GB', 'TB'][i]
        )
    }

    var sizeElements = document?.querySelectorAll('.filesize')
    sizeElements.forEach(sizeElement => {
        sizeElement.textContent = humanizeFileSize(
            parseInt(sizeElement.textContent.trim())
        )
    })

    var inputFile = document?.getElementById('dropzone-file')
    var fileNameDisplay = document?.getElementById('selected-file-display')

    inputFile?.addEventListener('change', event => {
        var selectedFile = event.target.files[0]

        if (selectedFile) {
            document
                ?.getElementById('upload-file-button')
                .classList.remove('hidden')
            document
                ?.getElementById('upload-details-minor')
                .classList.add('hidden')

            var p = document.createElement('p')
            p.className =
                'text-xs text-center text-gray-500 dark:text-gray-400 uppercase tracking-wider font-semibold'
            p.textContent = selectedFile.name
            fileNameDisplay.appendChild(p)
        }
    })

    var dirNameInput = document?.getElementById('dir_name')
    dirNameInput?.addEventListener('input', () => {
        var submitButton = document?.getElementById('create-folder-button')
        dirNameInput.value.length > 0
            ? submitButton?.removeAttribute('disabled')
            : submitButton?.setAttribute('disabled', 'true')
    })

    var deleteButtons = document?.querySelectorAll('#wants-to-delete')
    deleteButtons.forEach(deleteButton => {
        deleteButton.addEventListener('click', () => {
            document.getElementById('actively-deleted-name').textContent =
                localStorage.getItem('wants-to-delete')
        })
    })
})
