import axios from "axios";

const DB_BASEURL = "https://sd-db.glitch.me/";

function to(promise) {
  return promise
    .then(data => [data, undefined])
    .catch(error => Promise.resolve([undefined, error]));
}

async function getAllLogs(db_name) {
  let path = "/_all_docs?include_docs=true&conflicts=true";
  return await to(axios.get(DB_BASEURL + db_name + path));
}

module.exports = {
  getAllLogs
};
