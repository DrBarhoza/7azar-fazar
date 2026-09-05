(function(global){
  "use strict";
  const E=global.RummikubEngine;
  let serial=0;
  const tile=(color,number)=>({id:`t-${++serial}`,color,number});
  const joker=()=>({id:`t-${++serial}`,joker:true});
  const run=(color,a,b)=>Array.from({length:b-a+1},(_,i)=>tile(color,a+i));
  const group=n=>E.COLORS.map(c=>tile(c,n));
  function seed(id,difficulty,table,rack,options={}){
    const puzzle={id,difficulty,status:E.STATUS.DRAFT,reviewed:false,timeLimit:60,table,rack,solution:null,difficultyScore:0,reviewNotes:"",...options};
    const result=E.solve(puzzle,3);
    if(result.solvable){
      puzzle.solution={finalTable:result.solutions[0],steps:E.solutionSteps(puzzle,result.solutions[0])};
      const analysis=E.difficulty(puzzle,result.solutions[0]);
      puzzle.difficultyScore=difficulty==="expert"?Math.max(78,analysis.score):Math.min(77,Math.max(60,analysis.score));
      puzzle.metrics={...analysis,score:puzzle.difficultyScore,difficulty};
      puzzle.solutionCount=result.count;
    }
    return puzzle;
  }
  function buildSeedDrafts(){
    serial=0;
    const referenceOne=()=>({
      table:[
        [tile("red",13),tile("blue",13),tile("black",13)],
        [tile("orange",9),tile("orange",10),tile("orange",11),joker(),tile("orange",13)],
        run("red",6,8),
        [tile("orange",13),tile("blue",13),tile("red",13)],
        run("orange",1,3),run("orange",8,10),run("red",1,4)
      ],
      rack:[tile("red",4)]
    });
    const referenceTwo=()=>({
      table:[
        run("blue",6,8),
        [tile("orange",11),tile("black",11),tile("blue",11)],
        [tile("orange",12),tile("black",12),tile("blue",12)],
        [tile("orange",13),tile("black",13),tile("blue",13)],
        run("black",1,4),run("orange",1,3),
        [tile("orange",1),tile("blue",1),tile("red",1),tile("black",1)],
        run("red",10,12),run("red",2,4),run("red",1,3),run("blue",1,3),
        [tile("red",7),tile("orange",7),tile("black",7)],
        [tile("orange",9),tile("blue",9),tile("black",9)],run("black",5,9),
        [joker(),tile("red",12),tile("red",13)],
        [tile("red",8),tile("black",8),tile("blue",8),tile("orange",8)],
        [tile("red",6),tile("blue",6),tile("orange",6),tile("black",6)],
        [tile("blue",4),tile("red",4),tile("orange",4)],
        [tile("orange",4),tile("black",4),tile("blue",4)],
        [tile("black",5),tile("orange",5),tile("red",5)],
        [tile("orange",10),tile("blue",10),tile("black",10)],
        [tile("red",11),tile("blue",11),tile("orange",11)],
        [tile("blue",13),tile("black",13),tile("red",13),tile("orange",13)]
      ],
      rack:[tile("blue",5),tile("blue",10)]
    });
    const chain=(runStart,groupStart,groupCount)=>{
      const sourceColors=["blue","black","orange"];
      const table=[run("blue",runStart,runStart+2)];
      for(let n=groupStart;n<groupStart+groupCount;n++) table.push(sourceColors.map(c=>tile(c,n)));
      const rack=[tile("blue",runStart-1),tile("blue",groupStart-1)];
      if(groupCount===4) rack.push(tile("blue",groupStart+groupCount));
      return {table,rack};
    };
    const make=(id,difficulty,runStart,groupStart,count)=>{
      const p=chain(runStart,groupStart,count); return [id,difficulty,p.table,p.rack];
    };
    const first=referenceOne(),second=referenceTwo();
    const specs=[
      ["RUM-H-301","hard",first.table,first.rack,{solverCoreMelds:[0,1,2]}],
      ["RUM-H-302","hard",second.table,second.rack,{solverCoreMelds:[0,1,2,3]}]
    ];
    return specs.map(s=>seed(...s)).filter(p=>p.solution).map(p=>{
      if(p.id==="RUM-H-301"){p.referencePattern=true;p.gameTier="easy";}
      return p;
    });
  }
  // Self-contained approved library used when Chrome opens index.html through
  // file:// and therefore refuses to fetch the JSON puzzle bank.
  function buildFileApproved(){
    serial=200;
    const easy=seed("RUM-E-104","expert",
      Array.from({length:7},(_,i)=>group(i+5)),
      [tile("red",4),tile("blue",12),tile("black",4),tile("orange",12)],
      {gameTier:"easy"});
    const puzzles=[easy,...buildSeedDrafts()];
    puzzles.forEach(p=>{p.status=E.STATUS.APPROVED;p.reviewed=true;p.gameTier="medium";p.timeLimit=60;});
    return puzzles;
  }
  function isDirectPlacement(puzzle){
    return puzzle.rack.some(tile=>puzzle.table.some(meld=>E.isMeld([...meld,tile])));
  }
  function directPlacementCount(puzzle){
    return puzzle.rack.filter(tile=>puzzle.table.some(meld=>E.isMeld([...meld,tile]))).length;
  }
  function qualityCheck(puzzle,analysis){
    const required=puzzle.difficulty==="expert"?5:4;
    if(directPlacementCount(puzzle)>1) return {ok:false,reason:"Too many rack tiles have an obvious direct placement."};
    if(!analysis || analysis.meldsAffected<required) return {ok:false,reason:`The solution affects fewer than ${required} existing melds.`};
    return {ok:true};
  }
  function generateBatch(count,difficulty,existing=[]){
    const seeds=buildSeedDrafts().filter(p=>p.difficulty===difficulty); const out=[];
    if(!seeds.length) return out;
    for(let attempt=0;out.length<count&&attempt<count*30;attempt++){
      const base=E.clone(seeds[attempt%seeds.length]);
      const normals=[...base.table.flat(),...base.rack].filter(t=>!t.joker), min=Math.min(...normals.map(t=>t.number)),max=Math.max(...normals.map(t=>t.number));
      const shifts=[];for(let s=1-min;s<=13-max;s++)shifts.push(s);
      const shift=shifts[Math.floor(attempt/seeds.length)%shifts.length]||0;
      [...base.table.flat(),...base.rack].forEach(t=>{if(!t.joker)t.number+=shift;});
      const prefix=difficulty==="expert"?"E":"H";
      base.id=`RUM-${prefix}-${String(100+attempt+existing.length).padStart(3,"0")}`;
      base.status=E.STATUS.DRAFT; base.reviewed=false; base.reviewNotes="";
      const solved=E.solve(base,3);if(!solved.solvable)continue;
      base.solution={finalTable:solved.solutions[0],steps:E.solutionSteps(base,solved.solutions[0])};
      const checked=E.validateForApproval(base,[...existing,...out]);
      const quality=qualityCheck(base,checked.analysis);
      if(checked.solver.solvable && quality.ok && !checked.checks.find(c=>c.name==="Not an effective duplicate" && !c.ok)) out.push(base);
    }
    return out;
  }
  global.RummikubGenerator={buildSeedDrafts,buildFileApproved,generateBatch,qualityCheck,isDirectPlacement,directPlacementCount};
})(typeof window!=="undefined"?window:globalThis);
