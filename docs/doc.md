docker run -d -p 8000:8000 silvery886/freebili:1.0

sudo docker build -t freebili:1.25 .
sudo docker tag freebili:1.25 silvery886/freebili:1.25
sudo docker push silvery886/freebili:1.25


http://caiji.dyttzyapi.com/api.php/provide/vod/from/dyttm3u8/at/json?ac=detail&ids=8298 


window.location.hash = "keyword=凡人修仙传&douban_id=123456"

// 假设URL哈希值为 #keyword=凡人修仙传&douban_id=123456
let hashString = window.location.hash.substring(1); // 移除开头的 #
// hashString 现在是 "keyword=凡人修仙传&douban_id=123456"

let params = {};
hashString.split('&').forEach(pair => {
  let parts = pair.split('=');
  if (parts.length === 2) {
    let key = decodeURIComponent(parts[0]);
    let value = decodeURIComponent(parts[1]);
    params[key] = value;
  }
});

console.log(params); 