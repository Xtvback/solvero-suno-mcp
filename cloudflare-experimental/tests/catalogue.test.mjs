import assert from "node:assert/strict";
import {test} from "node:test";
import {listCatalogue,parseCatalogueManifest} from "../mcp-server/catalogue.ts";

const valid={version:1,owner_user_id:"synthetic-user",entries:[{
  id:"song-1",title:"Test",share_url:"https://suno.com/song/00000000-0000-4000-8000-000000000001",
  visibility:"link_only",source:"user_manifest",
}]};

test("catalogue accepts explicit metadata-only Suno share records",()=>{
 const manifest=parseCatalogueManifest(JSON.stringify(valid));
 assert.equal(listCatalogue(manifest).items.length,1);
});

test("catalogue rejects private audio fields, non-Suno URLs and duplicate ids",()=>{
 assert.throws(()=>parseCatalogueManifest(JSON.stringify({version:1,entries:[{...valid.entries[0],audio_url:"https://example.com/a.mp3"}]})),/Unsupported catalogue field/);
 assert.throws(()=>parseCatalogueManifest(JSON.stringify({version:1,entries:[{...valid.entries[0],share_url:"https://example.com/song/1"}]})),/HTTPS Suno share link/);
 assert.throws(()=>parseCatalogueManifest(JSON.stringify({version:1,owner_user_id:"synthetic-user",entries:[valid.entries[0],valid.entries[0]]})),/Duplicate catalogue id/);
});

test("non-empty catalogue requires an explicit owner binding",()=>{
 assert.throws(()=>parseCatalogueManifest(JSON.stringify({version:1,entries:valid.entries})),/owner_user_id is required/);
 assert.throws(()=>parseCatalogueManifest(JSON.stringify({...valid,private_audio:"forbidden"})),/Unsupported catalogue manifest field/);
});

test("catalogue query enforces bounded pagination",()=>{
 const manifest=parseCatalogueManifest(JSON.stringify(valid));
 assert.throws(()=>listCatalogue(manifest,{limit:101}),/1 to 100/);
 assert.throws(()=>listCatalogue(manifest,{cursor:"-1"}),/Invalid cursor/);
 assert.throws(()=>listCatalogue(manifest,{unknown:true}),/Unsupported argument/);
});
