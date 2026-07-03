// src/data/assets.js
import logoImage from '../assets/logo/ad_logo.png';
import bg_bx1 from '../assets/background/homebx1.avif';
import bg_bx3 from '../assets/background/home_bx3.jpg';

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

export const IMAGES = {
  logo: logoImage,
  heroBg: bg_bx1,
  heroBg3: bg_bx3,
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
  gif_webDev: gif_webDev
};