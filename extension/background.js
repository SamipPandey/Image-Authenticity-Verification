chrome.runtime.onInstalled.addListener(() => {
  console.log("Extension Installed - Creating Menu...");
  chrome.contextMenus.create({
    id: "verifyImage",
    title: "Verify Image Authenticity",
    contexts: ["image"]
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "verifyImage") {
    chrome.storage.local.set({ lastImageUrl: info.srcUrl }, () => {
      // This will open the popup automatically in some browsers
      // Or you can just manually click the icon after this
      console.log("Image URL saved:", info.srcUrl);
    });
  }
});