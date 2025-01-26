import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import PizzaForm from "./PizzaForm";

const menuItemStyles = {
  borderBottom: "1px solid #ccc",
  paddingBottom: "10px",
  marginBottom: "10px",
};

function Home() {
  const [restaurant, setRestaurant] = useState(null);
  const [status, setStatus] = useState("pending");
  const [error, setError] = useState(null);
  const { id } = useParams();

  useEffect(() => {
    let isMounted = true;

    fetch(`http://127.0.0.1:5555/restaurants/${id}`)
      .then((r) => {
        if (r.ok) {
          return r.json().then((data) => {
            if (isMounted) {
              setRestaurant(data);
              setStatus("resolved");
            }
          });
        } else {
          return r.json().then((err) => {
            if (isMounted) {
              setError(err.error || "An error occurred.");
              setStatus("rejected");
            }
          });
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(err.message);
          setStatus("rejected");
        }
      });

    return () => {
      isMounted = false;
    };
  }, [id]);

  function handleAddPizza(newRestaurantPizza) {
    setRestaurant((prev) => ({
      ...prev,
      restaurant_pizzas: [
        ...(prev?.restaurant_pizzas || []),
        newRestaurantPizza,
      ],
    }));
  }

  if (status === "pending") return <h1>Loading...</h1>;
  if (status === "rejected") return <h1>Error: {error}</h1>;

  return (
    <section className="container">
      <div className="card">
        <h1>{restaurant.name}</h1>
        <p>{restaurant.address}</p>
      </div>
      <div className="card">
        <h2>Pizza Menu</h2>
        {Array.isArray(restaurant.restaurant_pizzas) && restaurant.restaurant_pizzas.length > 0 ? (
          restaurant.restaurant_pizzas.map((restaurant_pizza) => (
            <div key={restaurant_pizza.id} style={menuItemStyles}>
              <h3>{restaurant_pizza.pizza.name}</h3>
              <p>
                <em>{restaurant_pizza.pizza.ingredients}</em>
              </p>
              <p>
                <strong>Price: ${restaurant_pizza.price}</strong>
              </p>
            </div>
          ))
        ) : (
          <p>No pizzas available at this restaurant.</p>
        )}
      </div>
      <div className="card">
        <h3>Add New Pizza</h3>
        <PizzaForm restaurantId={restaurant.id} onAddPizza={handleAddPizza} />
      </div>
    </section>
  );
}

export default Home;
