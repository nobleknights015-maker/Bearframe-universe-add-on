// A timed-out chunk ticket may resolve later. Give each attempt its own name,
// and release late tickets without touching a newer request.
export async function withTemporaryArea({areas,dimension,from,to,name,task,scheduleTimeout,cancelTimeout}){
 let timer,closed=false;
 const remove=()=>{if(areas.hasTickingArea(name))areas.removeTickingArea(name);};
 try{
  const pending=Promise.resolve(areas.createTickingArea(name,{dimension,from,to})).then(value=>{
   if(closed)remove();
   return value;
  });
  await Promise.race([pending,new Promise((_,reject)=>{
   timer=scheduleTimeout(()=>reject(Error("Chunk loading timed out for "+name)));
  })]);
  return await task();
 }finally{
  closed=true;
  if(timer!==undefined)cancelTimeout(timer);
  remove();
 }
}
