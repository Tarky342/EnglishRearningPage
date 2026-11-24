export const TUTOR_SCHEMA={
  type:'object',
  properties:{
    title:{type:'string'},explanation:{type:'string'},keyPoint:{type:'string'},hint:{type:'string'},
    check:{type:'object',properties:{stem:{type:'string'},choices:{type:'array',items:{type:'string'}},answerIndex:{type:'integer'},reasoning:{type:'string'}},required:['stem','choices','answerIndex','reasoning'],additionalProperties:false}
  },
  required:['title','explanation','keyPoint','hint','check'],
  additionalProperties:false
};
export function validateTutorOutput(v,originalStem){
  if(!v||typeof v!=='object')return false;
  for(const x of ['title','explanation','keyPoint','hint'])if(typeof v[x]!=='string'||!v[x].trim()||v[x].length>900)return false;
  const c=v.check;
  if(!c||typeof c!=='object'||typeof c.stem!=='string'||c.stem.trim().length<10||c.stem.length>400)return false;
  if(c.stem.trim()===originalStem.trim())return false;
  if(!Array.isArray(c.choices)||c.choices.length!==2||c.choices.some(x=>typeof x!=='string'||!x.trim()||x.length>180))return false;
  if(c.choices[0]===c.choices[1]||![0,1].includes(c.answerIndex))return false;
  if(typeof c.reasoning!=='string'||!c.reasoning.trim()||c.reasoning.length>500)return false;
  return true;
}
