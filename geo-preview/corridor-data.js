/* Century of Empires: geography-first corridor data.
   Site coordinates are modern gazetteer points, not 1780 surveying.
   The north-south corridor is historically documented; individual route
   vertices are an UNVERIFIED PROVISIONAL sketch, not archival road traces.
   Replace route vertices only with sourced, audited historical geometry. */
(function(root,factory){
 const data=factory();
 if(typeof module==="object"&&module.exports)module.exports=data;
 else root.COEGeographyData=data;
})(typeof globalThis!=="undefined"?globalThis:this,function(){
 "use strict";
 const settlements=[
  {id:"innsbruck",name:"Innsbruck",point:[11.3936,47.2680],confidence:"gazetteer location"},
  {id:"schoenberg",name:"Schönberg",point:[11.4061,47.1864],confidence:"gazetteer location"},
  {id:"matrei",name:"Matrei am Brenner",point:[11.4531,47.1308],confidence:"gazetteer location"},
  {id:"steinach",name:"Steinach",point:[11.4667,47.0833],confidence:"gazetteer location"},
  {id:"gries",name:"Gries am Brenner",point:[11.5000,47.0500],confidence:"approximate locality"},
  {id:"brenner",name:"Brenner Pass",point:[11.50836,47.00528],confidence:"gazetteer location"},
  {id:"gossensass",name:"Gossensass",point:[11.4448,46.9383],confidence:"gazetteer location"}
 ];
 const corridors=[{
  id:"wipptal-provisional-01",
  name:"Wipptal–Brenner corridor (provisional trace)",
  certainty:"historical corridor documented; exact 1780–1880 cartway line not established",
  provenance:"Illustrative connecting vertices, NOT surveyed historic road or OSM routing.",
  coordinates:[
   [11.3936,47.2680],[11.4000,47.2520],[11.4090,47.2370],
   [11.4200,47.2220],[11.4220,47.2070],[11.4150,47.1960],
   [11.4061,47.1864],[11.4130,47.1750],[11.4220,47.1650],
   [11.4290,47.1500],[11.4420,47.1400],[11.4531,47.1308],
   [11.4540,47.1190],[11.4600,47.1050],[11.4667,47.0833],
   [11.4780,47.0710],[11.4900,47.0610],[11.5000,47.0500],
   [11.5050,47.0360],[11.5100,47.0210],[11.50836,47.00528],
   [11.5000,46.9900],[11.4860,46.9750],[11.4700,46.9610],
   [11.4550,46.9460],[11.4448,46.9383]
  ]
 }];
 return Object.freeze({
  period:"1780–1880",region:"Matrei am Brenner / Wipptal / Brenner Pass",
  status:"GEOGRAPHIC DEMONSTRATOR — cartway trace provisional",
  settlements,corridors,
  sources:[
   "https://www.wipptal.at/en/your-wipptal/the-wipptal-valley/matrei-am-brenner",
   "https://www.geonames.org/2781423/brenner-pass.html",
   "https://www.geonames.org/2764557/steinach-am-brenner.html",
   "https://www.geonames.org/2765715/schoenberg-im-stubaital.html",
   "https://www.geonames.org/2764557/steinach-am-brenner.html"
  ]
 });
});