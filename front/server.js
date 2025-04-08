const express = require("express");
const cors = require("cors");
const app = express();
const port = 8000;
const path = require("path");

app.use(express.static(path.join(__dirname, "public")));

app.get("/book", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "page1.html"));
});

app.get("/login", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "login.html"));
});
app.get("/register", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "register.html"));
});

app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "rooms.html"));
});

app.listen(port, () => {
  console.log(`Server is running at http://localhost:${port}`);
});
