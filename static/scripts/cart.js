// Cart buttons: any element with data-cart-action and data-product-id updates the cart in place.

const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

async function updateCart(productId, action) {
  const response = await fetch("/cart/update/", {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken },
    body: JSON.stringify({ product_id: productId, action }),
  });
  if (!response.ok) {
    throw new Error(`Cart update failed with status ${response.status}`);
  }
  return response.json();
}

function renderCart(productId, cart) {
  document.querySelectorAll("[data-cart-count]").forEach((badge) => {
    badge.textContent = cart.cart_count;
  });
  document.querySelectorAll("[data-cart-total]").forEach((total) => {
    total.textContent = cart.cart_total;
  });

  const line = document.querySelector(`[data-cart-line="${productId}"]`);
  if (line === null) {
    return;
  }
  if (cart.quantity === 0) {
    line.remove();
    if (cart.cart_count === 0) {
      window.location.reload();
    }
    return;
  }
  line.querySelector("[data-line-quantity]").textContent = cart.quantity;
  line.querySelector("[data-line-total]").textContent = cart.line_total;
}

document.addEventListener("click", async (event) => {
  const button = event.target.closest("[data-cart-action]");
  if (button === null) {
    return;
  }
  const { productId, cartAction } = button.dataset;
  button.disabled = true;
  try {
    renderCart(productId, await updateCart(productId, cartAction));
  } catch (error) {
    console.error(error);
    window.alert("Sorry, the cart could not be updated. Please try again.");
  } finally {
    button.disabled = false;
  }
});
