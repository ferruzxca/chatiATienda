const $ = (q) => document.querySelector(q);

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
const csrf = getCookie('csrftoken');

function addMsg(text, cls="bot"){
  const div = document.createElement("div");
  div.className = cls;
  div.textContent = text;
  $("#messages").appendChild(div);
  $("#messages").scrollTop = $("#messages").scrollHeight;
}

async function sendMessage(text){
  addMsg(text, "me");
  const res = await fetch("/api/message/", {
    method: "POST",
    headers: {"Content-Type": "application/x-www-form-urlencoded", "X-CSRFToken": csrf || ""},
    body: new URLSearchParams({message: text})
  });
  const data = await res.json();
  if (data.reply) addMsg(data.reply, "bot");
  if (data.cart_html) $("#cart-area").innerHTML = data.cart_html;
  renderSuggestions(data.suggestions || []);
}

function renderSuggestions(suggs){
  const box = $("#suggestions");
  box.innerHTML = "";
  suggs.forEach(s => {
    const chip = document.createElement("div");
    chip.className = "chip";
    chip.textContent = s.text;
    chip.onclick = async () => {
      const r = await fetch(`/api/add/?sku=${encodeURIComponent(s.sku)}&qty=1`);
      const d = await r.json();
      if (d.reply) addMsg(d.reply, "bot");
      if (d.cart_html) $("#cart-area").innerHTML = d.cart_html;
    };
    box.appendChild(chip);
  });
}

$("#chat-form").addEventListener("submit", (e)=>{
  e.preventDefault();
  const v = $("#chat-input").value.trim();
  if(!v) return;
  $("#chat-input").value = "";
  sendMessage(v);
});
