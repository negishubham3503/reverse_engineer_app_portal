(function waitForJava() {
  if (typeof Java !== "undefined" && Java.available) {
    Java.perform(function () {
      send("Java available, hooks can be placed now");
      // put hooks here
    });
  } else {
    setTimeout(waitForJava, 300);
  }
})();