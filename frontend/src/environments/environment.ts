/* @TODO replace with your variables
 * ensure all variables on this page match your project
 */

export const environment = {
  production: false,
  apiServerUrl: "http://127.0.0.1:5000", // the running FLASK api server url
  auth0: {
    url: "dev-xp3i9c1n.us", // the auth0 domain prefix
    audience: "https://dev-xp3i9c1n.us.auth0.com/api/v2/", // the audience set for the auth0 app
    clientId: "ZQ1pfeSK6mIfm7NhaP5HnaNq51GGPDqn", // the client id generated for the auth0 app
    callbackURL: "http://localhost:8100", // the base url of the running ionic application.
  },
};
