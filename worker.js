import{validate}from"./luau-core.js";
import rules from"./rules.json";
const H={"access-control-allow-origin":"*","access-control-allow-headers":"content-type","content-type":"application/json"};
const J=(o,s=200)=>new Response(JSON.stringify(o),{status:s,headers:H});
export default{async fetch(req){
  const u=new URL(req.url);
  if(req.method==="OPTIONS")return new Response(null,{headers:H});
  if(u.pathname==="/rules")return J(rules);
  if(u.pathname==="/validate"){
    let code=u.searchParams.get("code");
    if(req.method==="POST"){try{code=(await req.json()).code}catch{return J({error:"JSON body {code} chahiye"},400)}}
    if(typeof code!=="string"||code.length>200000)return J({error:"code missing ya bahut bada (max 200KB)"},400);
    return J(validate(code,rules.rules))}
  return J({endpoints:["POST /validate {code}","GET /validate?code=","GET /rules"]})}};
