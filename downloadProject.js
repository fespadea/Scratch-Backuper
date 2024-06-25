const SBDL = require('@turbowarp/sbdl');

const options = {
    // May be called periodically with progress updates.
    onProgress: (type, loaded, total) => {
        // type is 'metadata', 'project', 'assets', or 'compress'
        console.log(type, loaded / total);
    }
};

module.exports =  async function downloadProject() {
    const project = await SBDL.downloadProjectFromID('1582245', options);
    console.log(project)
    c
    project
  }
