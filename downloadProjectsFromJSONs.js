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
  const jsonPath = "./projectJsons/"
  const projectsToDownload = fs.readdirSync(jsonPath);
  const saveLocation = "./projectsDownloadedFromJsons/"
  const downloadedProjects = fs.readdirSync(saveLocation);
  for(let i = 0; i < downloadedProjects.length; i++){
    downloadedProjects[i] = downloadedProjects[i].replace(/\.[^/.]+$/, "")
  }
  const numProjects = projectsToDownload.length - downloadedProjects.length
  let projectCounter = 0;

  for (const projectJson of projectsToDownload) {
    const projectName = projectJson.substring(0, projectJson.indexOf(".json"))
    if(!downloadedProjects.includes(projectName)){
        const project = await SBDL.downloadProjectFromJSON(fs.readFileSync(jsonPath + projectJson, 'utf-8'), options);
        fs.writeFile(saveLocation + projectName + "." + project.type, Buffer.from(project.arrayBuffer), { flag: 'w' }, (err) => {
            if (err) console.log(err);
          });
        console.log(`${++projectCounter} / ${numProjects}: ${project.title}`)
    }
  }

  console.log("Done");
}

downloadProjects();
