window.addEventListener("load", function () {
  var currentDirEl = document?.getElementById("name_for_current_directory");
  var tdElements = document?.querySelectorAll(".timestamps");
  tdElements.forEach((td) => {
    var rawTimestamp = td.textContent.trim();
    var date = new Date(rawTimestamp);
    var options = {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "numeric",
      minute: "numeric",
      hour12: true,
    };
    td.textContent = date.toLocaleString("en-US", options);
  });

  const humanizeFileSize = (size) => {
    const i = size === 0 ? 0 : Math.floor(Math.log(size) / Math.log(1024));
    return (
      (size / Math.pow(1024, i)).toFixed(2) * 1 +
      " " +
      ["B", "kB", "MB", "GB", "TB"][i]
    );
  };

  var sizeElements = document?.querySelectorAll(".filesize");
  sizeElements.forEach((sizeElement) => {
    sizeElement.textContent = humanizeFileSize(
      parseInt(sizeElement.textContent.trim()),
    );
  });

  var inputFile = document?.getElementById("dropzone-file");
  var fileNameDisplay = document?.getElementById("selected-file-display");

  inputFile?.addEventListener("change", (event) => {
    var selectedFile = event.target.files[0];

    if (selectedFile) {
      document?.getElementById("upload-file-button").classList.remove("hidden");
      document?.getElementById("upload-details-minor").classList.add("hidden");

      var p = document.createElement("p");
      p.className =
        "text-xs text-center text-gray-500 dark:text-gray-400 uppercase tracking-wider font-semibold";
      p.textContent = selectedFile.name;
      fileNameDisplay.appendChild(p);
    }
  });

  var dirNameInput = document?.getElementById("dir_name");
  dirNameInput?.addEventListener("input", () => {
    var submitButton = document?.getElementById("create-folder-button");
    dirNameInput.value.length > 0
      ? submitButton?.removeAttribute("disabled")
      : submitButton?.setAttribute("disabled", "true");
  });

  var deleteButtons = document?.querySelectorAll("#wants-to-delete");
  deleteButtons.forEach((deleteButton) => {
    deleteButton.addEventListener("click", () => {
      document.getElementById("actively-deleted-name").textContent =
        localStorage.getItem("wants-to-delete");
    });
  });

  var subStorageTable = document?.getElementById("sub-storage-table");
  var storageTable = document?.getElementById("storage-table");

  if (subStorageTable) {
    storageTable && storageTable.classList.add("hidden");

    var subDirs = document?.querySelectorAll(".sub_dir_name_getter");
    var checkAgainst = document?.querySelectorAll("#get_sub_dir_name")[0].value;

    //Workaround for the current directory
    if (localStorage.getItem("current_directory") !== checkAgainst) {
      localStorage.setItem("current_directory", checkAgainst);
      var c = localStorage.getItem("current_directory");
      console.log({ checkAgainst, c });
    }
    currentDirEl.textContent = localStorage.getItem("current_directory");
    var oneDirBackward = goBackOneDir();
    console.log(oneDirBackward);
    assignGoBackOneDirToButton(oneDirBackward);
    var deleteFilePrefixPath = document?.querySelectorAll(
      "#delete-file-prefix",
    );
    deleteFilePrefixPath.forEach((path) => {
      console.log("B4", path);
      path.value = currentDirEl.textContent;
      console.log("AFTA", path);
    });
    document
      ?.querySelectorAll("#sub-dir-storage-table")[0]
      .classList.add("hidden");

    subDirs.forEach((dir) => {
      if (dir.value) {
        var initialValue = dir.value;
        dir.value = removeCurrentDirPrefixFromViewString(initialValue);
      } else if (dir.textContent) {
        var initialValue = dir.textContent;
        dir.textContent = removeCurrentDirPrefixFromViewString(initialValue);
      }
    });
  }

  var getPhotos = window.location.href.includes("/get-photos");
  if (getPhotos) {
    document.getElementById("gallery")?.classList.remove("hidden");
    document.getElementById("uploading_dock")?.classList.add("hidden");
  }
});

const removeCurrentDirPrefixFromViewString = (viewString) => {
  var currentDir = localStorage.getItem("current_directory").length;
  return viewString.substring(currentDir);
};

const assignGoBackOneDirToButton = (whichDirectory) => {
  var input = document.getElementById("go_back_dir");
  input.value = whichDirectory;
};

const goBackOneDir = () => {
  var currentDir = localStorage.getItem("current_directory");
  var currentDirArray = currentDir.split("/");
  if (currentDirArray.length === 2) {
    return "/";
  }
  currentDirArray.pop();
  currentDirArray.pop();
  var newCurrentDir = currentDirArray.join("/");
  console.log(newCurrentDir);
  return newCurrentDir + "/";
};
