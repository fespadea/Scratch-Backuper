const SBDL = require("@turbowarp/sbdl");
const fs = require("node:fs");

const downloadProjects = async function() {
  const options = {
    // May be called periodically with progress updates.
    onProgress: (type, loaded, total) => {
      // type is 'metadata', 'project', 'assets', or 'compress'
      console.log(type, loaded / total);
    },
  };
  
  const authData = require("./scratchAuthenticationToken.json");
  const projectsToDownload = require("./" + authData["username"] +
    " projects (including descended).json");
  const numProjects = Object.keys(projectsToDownload).length
  let projectCounter = 0;

  for (const projectID of Object.keys(projectsToDownload)) {
    const project = await SBDL.downloadProjectFromID(projectID, options);
    for (const saveLocation of projectsToDownload[projectID]) {
      fs.writeFile(saveLocation + project.title + "." + project.type, Buffer.from(project.arrayBuffer), { flag: 'w' }, (err) => {
        if (err) console.log(err);
      });
    }
    console.log(`${++projectCounter} / ${numProjects}: ${project.title}`)
  }
}

downloadProjects();
console.log("Done")
