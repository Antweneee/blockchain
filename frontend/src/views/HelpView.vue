<template>
  <div class="tutorial-page">
    <header>
      <div class="header-content">
        <h1>Welcome to our tokenized asset platform</h1>
        <p>
          Discover how to buy, sell, and trade real estate as NFTs using the XRP Ledger blockchain.
        </p>
      </div>
    </header>

    <section class="objective">
      <h2>Our Mission</h2>
      <p>
        Our goal is to enable the tokenization and secure exchange of real-world assets, such as real estate properties, by representing them as digital tokens (NFTs) on the XRP Ledger blockchain.
      </p>
    </section>

    <section class="how-to">
      <h2>How to use the platform?</h2>

      <div class="step step-margin" v-for="(step, index) in steps" :key="index">
        <h3>Step {{ index + 1 }}: {{ step.title }}</h3>
        <p>{{ step.description }}</p>
        <img :src="step.image" :alt="`Step ${index + 1} image`" class="step-image" />
      </div>

      <div class="step">
        <h3>Browse and buy assets in the marketplace</h3>
        <p>
          Visit the marketplace to explore available assets, cancel listings, or make purchases.
        </p>
        <img :src="images.marketplace" :alt="`Marketplace image`" class="step-image" />
      </div>

      <div class="step">
        <h3>Manage your assets in the wallet</h3>
        <p>
          Use the wallet page to view and manage your tokenized assets securely.
        </p>
        <img :src="images.wallet" :alt="`Wallet image`" class="step-image" />
      </div>
    </section>

    <section class="faq">
      <h2>FAQ</h2>
      <details v-for="(faq, index) in faqs" :key="index">
        <summary>{{ faq.question }}</summary>
        <p>{{ faq.answer }}</p>
      </details>
    </section>

    <footer>
      <p>
        Need help? Check out our <a href="#">user guide</a> or reach out to our support team.
      </p>
    </footer>
  </div>
</template>

<script>
import step1Image from '../assets/dashboard.png';
import step2Image from '../assets/new_asset.png';
import step3Image from '../assets/list_asset.png';
import step4Image from '../assets/marketplace.png';
import step5Image from '../assets/wallet.png';

export default {
  data() {
    return {
      images: {
        marketplace: step4Image,
        wallet: step5Image,
      },
      steps: [
        {
          title: "Tokenize a property",
          description:
            "Click on 'Tokenize New Asset' to start the process of tokenizing your property.",
          image: step1Image,
        },
        {
          title: "Add property details",
          description:
            "Fill in your property details, such as title, description, transfer fee, and an image. Then click 'Create Token'.",
          image: step2Image,
        },
        {
          title: "List your property",
          description:
            "Set a price for your property and click 'Create Listing' to make it available for sale.",
          image: step3Image,
        },
      ],
      faqs: [
        {
          question: "What is a real estate NFT?",
          answer:
            "It's a unique digital token that represents ownership of a real estate property on the blockchain.",
        },
        {
          question: "How does the platform ensure security?",
          answer:
            "We use the XRP Ledger blockchain to provide secure, immutable transactions and protect user data with advanced security measures.",
        },
        {
          question: "Can I sell multiple properties?",
          answer:
            "Yes, you can tokenize and list as many properties as you like, provided they comply with our terms.",
        },
        {
          question: "How do I get started?",
          answer:
            "Sign up on our platform, connect your wallet, and follow the steps to tokenize and list your property.",
        },
        {
          question: "Are there any fees for transactions?",
          answer:
            "Yes, a small transaction fee is required for blockchain operations. Detailed fee structures are available in our user guide.",
        },
      ],
    };
  },
};
</script>

<style scoped>
.tutorial-page {
  font-family: Arial, sans-serif;
  line-height: 1.6;
  padding: 20px;
  background-color: #f9fafb;
}

header {
  text-align: center;
  margin-bottom: 30px;
  display: flex;
  justify-content: center;
}

.header-content {
  background-color: white;
  width: fit-content;
  border-radius: 20px;
  padding: 10px 50px;
}

header h1 {
  font-size: 2em;
  margin: 0;
  color: rgb(99 102 241 / var(--tw-text-opacity, 1));
}

header p {
  font-size: 1.2em;
}

section {
  margin-bottom: 40px;
  background-color: white;
  border-radius: 20px;
  padding: 10px 30px;
}

section h2 {
  font-size: 1.8em;
  margin: 0 0 10px;
  color: rgb(99 102 241 / var(--tw-text-opacity, 1));
}

.step {
  margin-bottom: 20px;
}

.step-margin {
  margin-bottom: 20px;
  margin-left: 50px;
}

.step-image {
  max-width: 100%;
  height: auto;
  margin-bottom: 10px;
  border: 1px solid black;
  border-radius: 10px;
}

.step h3 {
  font-size: 1.4em;
  color: rgb(99 102 241 / var(--tw-text-opacity, 1));
  margin-bottom: 5px;
}

.faq details {
  margin-bottom: 10px;
}

.faq summary {
  font-weight: bold;
  cursor: pointer;
  color: rgb(99 102 241 / var(--tw-text-opacity, 1));
}

.faq p {
  margin-left: 20px;
}

footer {
  text-align: center;
  margin-top: 20px;
  font-size: 0.9em;
}

footer a {
  color: rgb(99 102 241 / var(--tw-text-opacity, 1));
  text-decoration: none;
}

footer a:hover {
  text-decoration: underline;
}
</style>