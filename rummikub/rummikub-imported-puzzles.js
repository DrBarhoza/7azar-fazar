(function(global){
  "use strict";
  let serial=0;
  const color={r:"red",b:"blue",k:"black",o:"orange"};
  function tile(code){
    if(code==="j")return{id:`shot-${++serial}`,joker:true};
    return{id:`shot-${++serial}`,color:color[code[0]],number:Number(code.slice(1))};
  }
  const meld=text=>text.trim().split(/\s+/).map(tile);
  function puzzle(id,title,gameTier,table,rack){
    const difficulty=gameTier==="expert"?"expert":"hard";
    const timeLimit=gameTier==="easy"?30:gameTier==="medium"?60:120;
    return{id,title,difficulty,gameTier,status:"approved",reviewed:true,timeLimit,
      table:table.map(meld),rack:meld(rack),solution:null,referencePattern:true,
      reviewNotes:"Manually transcribed from the user's reference screenshot for private play testing."};
  }
  function build(){
    serial=0;
    const puzzles=[
      puzzle("RUM-H-401","Put yellow 6 only","easy",[
        "b6 b7 b8 b9 b10 b11","r8 o8 b8","k13 o13 r13","k12 o12 b12","k1 k2 k3",
        "k5 k6 k7","b3 o3 r3","r11 r12 r13","b9 b10 b11","k7 b7 o7 r7",
        "r5 r6 r7","r8 o8 k8","r9 r10 r11","k4 r4 o4","r1 r2 r3 r4 r5"
      ],"o6"),
      puzzle("RUM-H-402","All except black 5","hard",[
        "o6 o7 o8","b9 k9 o9","o5 k5 r5","r12 o12 b12","r8 r9 r10 r11",
        "o2 o3 o4","k9 o9 r9","k1 o1 b1 r1","r1 k1 o1","b3 k3 r3",
        "b4 b5 b6 b7","b7 b8 b9 b10","b11 k11 r11 o11","o10 o11 o12",
        "r6 k6 b6","b1 b2 b3 b4","k10 r10 o10","k8 r8 b8","b10 b11 b12",
        "k11 k12 k13","r13 k13 o13"
      ],"o2 o4 o8 r2 j k8 r7"),
      puzzle("RUM-H-403","Finish all — medium","medium",[
        "b13 o13 r13","r7 r8 r9 j r11","k10 o10 r10","k1 k2 k3 k4 k5 k6 k7",
        "o9 b9 k9","b3 b4 b5","b5 b6 b7 b8 b9","r12 k12 b12","k11 o11 r11",
        "k7 o7 r7","o8 o9 o10 o11 o12","o3 r3 k3","k4 o4 r4","o6 o7 o8","b12 r12 o12"
      ],"o2 k2 b13 r5 j"),
      puzzle("RUM-H-404","Put all","easy",[
        "b8 o8 r8","b9 b10 b11 b12","k13 r13 b13","o10 b10 r10","o5 k5 b5",
        "o11 o12 o13","k8 k9 k10 k11 k12 k13","o5 b5 r5","k2 b2 r2 o2",
        "k12 b12 o12","k7 k8 k9 k10","k1 k2 k3 k4 k5","b3 j r3",
        "r8 r9 r10 r11 r12 r13","o6 o7 o8 o9","r6 k6 b6 o6","o7 b7 r7 k7",
        "b9 r9 o9","r3 r4 r5 r6","b3 o3 k3","k11 o11 r11"
      ],"r4 o3 b7 b1 r1"),
      puzzle("RUM-H-405","Put 11","medium",[
        "b9 b10 b11","r3 r4 r5","r5 r6 r7","k11 k12 k13","o2 o3 o4",
        "b11 b12 b13","o13 b13 r13","b3 b4 b5","o1 k1 b1","b4 b5 b6 b7",
        "r6 k6 o6","r7 r8 r9 r10 r11","k10 r10 b10","o2 b2 k2 r2",
        "k8 o8 r8","o7 o8 o9","o11 o12 o13","r1 o1 k1","j o6 o7"
      ],"r11"),
      puzzle("RUM-H-406","Put the 1","medium",[
        "k8 k9 k10","k2 k3 k4 k5","k2 b2 o2","r6 b6 k6","o12 b12 r12",
        "b3 j o3","r4 r5 r6","k7 o7 b7","k11 b11 o11","o13 r13 k13 b13",
        "b3 b4 b5 b6","o4 o5 o6 o7 o8","k12 b12 o12","k9 b9 r9",
        "k7 b7 r7","b9 b10 b11","o10 b10 r10 k10"
      ],"b1"),
      puzzle("RUM-H-407","Finish all","easy",[
        "b9 b10 b11","b4 b5 b6","o12 b12 r12","r7 k7 b7","r9 o9 k9",
        "b8 o8 k8","k4 k5 k6","b11 r11 o11","o3 o4 o5","o7 o8 o9",
        "k11 k12 k13","k2 b2 o2","k1 o1 b1 r1","b13 r13 o13",
        "k2 o2 r2","k4 k5 k6","b4 j b6","o10 k10 b10"
      ],"r8 r6"),
      puzzle("RUM-H-408","Finish all — hard","hard",[
        "b4 b5 b6","o12 b12 r12","r7 k7 b7","r9 o9 k9","b8 o8 k8",
        "k4 k5 k6","b11 r11 o11","b9 b10 b11","o4 o5 j o7 o8 o9 o10",
        "k10 k11 k12","k2 b2 o2","k1 o1 b1 r1","b13 r13 o13 k13",
        "k2 o2 r2","k4 k5 k6"
      ],"r1 r6 b10"),
      puzzle("RUM-H-409","Finish all — easy","easy",[
        "r10 r11 r12","r10 k10 b10","b5 b6 b7 b8 b9 b10","k5 o5 r5",
        "k4 r4 b4 o4","b3 o3 r3","o9 r9 k9","k6 b6 o6","b13 k13 r13",
        "k2 o2 r2","k12 o12 b12","r4 r5 r6 r7 r8","k6 k7 k8 k9",
        "k10 k11 k12 k13","b5 k5 o5","r11 b11 o11 k11","o13 r13 b13","o6 o7 o8 o9"
      ],"k1 k2 k3 r1 o1 r1 o12 j r9"),
      puzzle("RUM-E-410","All — very hard","expert",[
        "b10 o10 r10","k9 b9 o9","r8 o8 k8","k2 k3 k4","r12 b12 o12",
        "k5 k6 k7","k6 k7 k8 k9 k10 k11","b5 o5 k5","r9 r10 r11 r12",
        "b6 o6 r6","r4 b4 o4","b7 b8 b9","k1 o1 r1","r1 o1 k1",
        "k2 b2 o2","o8 b8 r8","k13 b13 o13","k3 b3 o3","o7 j o9 o10",
        "k11 b11 o11","r2 r3 r4 r5 r6"
      ],"r7 o3 b13 k13 b6 b1 r7 o11 o12")
    ];
    const cores={
      "RUM-H-401":[0,1,9,10],
      "RUM-H-402":[0,8,10,14,15,17],
      "RUM-H-403":[7,10,11,12],
      "RUM-H-404":[7,11,12,15],
      "RUM-H-405":[3,5,16],
      "RUM-H-406":[5,11],
      "RUM-H-407":[1,3,6],
      "RUM-H-408":[0,5,8,9,11,12],
      "RUM-H-409":[0,4,5,12,13,14,16],
      "RUM-E-410":[3,5,11,12,14,18,20]
    };
    if(global.RummikubEngine){
      puzzles.forEach(p=>{
        p.solverCoreMelds=cores[p.id];
        const solved=global.RummikubEngine.solve(p,1);
        if(solved.solvable){
          const finalTable=solved.solutions[0];
          p.solution={finalTable,steps:global.RummikubEngine.solutionSteps(p,finalTable)};
          p.solutionCount=solved.count;
        }
      });
    }
    return puzzles;
  }
  global.RummikubImportedPuzzles={build};
})(typeof window!=="undefined"?window:globalThis);
