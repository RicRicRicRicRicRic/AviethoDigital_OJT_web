// src/data/assets.js
import logoImage from '../assets/logo/ad_logo.png';
import bg_bx1 from '../assets/background/homebx1.avif';
import bg_bx3 from '../assets/background/home_bx3.jpg';
import bg_bx5 from '../assets/imgs/fb_page.png';
import team_bg_bx4 from '../assets/background/team_bg.jpg';

// Partners
import aviethoImage from '../assets/partners/avietho.png';
import cupangImage from '../assets/partners/cupang.png';
import landcoImage from '../assets/partners/Landco.png';
import manOfTheWorldImage from '../assets/partners/man_of_the_world.png';
import missWorldBatangasImage from '../assets/partners/miss_world_batangas.png';
import r18Image from '../assets/partners/r-18.png';

// Features
import mmBranding from '../assets/imgs/mm_branding.jpg';
import mmMarketing from '../assets/imgs/mm_marketing.webp';
import publicRelations from '../assets/imgs/public_relations.jpg';
import webDev from '../assets/imgs/web_dev.webp';

import gif_webDev from '../assets/gifs/gif_web_dev.gif';

import teamRickie from '../assets/imgs/teamRickie.png';
import teamJojo from '../assets/imgs/teamJojo.png';
import teamMigz from '../assets/imgs/teamMigz.png';
import teamMike from '../assets/imgs/teamMike.png';

import yt from '../assets/icon/yt_icon.png';
import tktk from '../assets/icon/tiktok_icon.png';
import ig from '../assets/icon/insta_icon.png';
import fb from '../assets/icon/fb_icon.webp';

import s1 from '../assets/imgs/slide1.jpg';
import s2 from '../assets/imgs/slide2.jpg';
import s3 from '../assets/imgs/slide3.jpg';
import s4 from '../assets/imgs/slide4.jpg';
import s5 from '../assets/imgs/slide5.jpg';
import s6 from '../assets/imgs/slide6.jpg';
import s7 from '../assets/imgs/slide7.jpg';
import s8 from '../assets/imgs/slide8.jpg';
import s9 from '../assets/imgs/slide9.jpg';
import s10 from '../assets/imgs/slide10.jpg';
import s11 from '../assets/imgs/slide11.jpg';

export const IMAGES = {
  logo: logoImage,
  heroBg: bg_bx1,
  heroBg3: bg_bx3,
  heroBg5: bg_bx5,
  teamBgbx4: team_bg_bx4,
  partners: [
    aviethoImage,
    cupangImage,
    landcoImage,
    manOfTheWorldImage,
    missWorldBatangasImage,
    r18Image
  ],
  services: {
    publicRelations,
    mmMarketing,
    mmBranding,
    webDev
  },
  gif_webDev: gif_webDev,
  team: {
    rickie: teamRickie,
    jojo: teamJojo,
    migz: teamMigz,
    mike: teamMike
  },
  icon:{
    yt,
    tktk,
    ig,
    fb
  },
  slide:{
    s1,
    s2,
    s3,
    s4,
    s5,
    s6,
    s7,
    s8,
    s9,
    s10,
    s11
  }
};