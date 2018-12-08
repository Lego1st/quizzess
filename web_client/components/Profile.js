import React from 'react';
import Ranking from './Ranking';
import GeneralInfo from './GeneralInfo';
import StatsChart from './StatsChart';
import ProfileSideBar from './ProfileSideBar';
import { Link } from 'react-router-dom';
import get_data from './Utils';

class Profile extends React.Component {
  constructor(props) {
    super(props);
    this.state = { is_editing: false }
  }
  handle_save() {
    this.setState({ is_editing: false });
  }
  render() {

    return (
      <div className="container" id="profile-page">
        <div className="row">
          <ProfileSideBar username={this.props.match.params.username} />
          <div className="col-md-7">
                
                <div className='title'>          
                  <h4 style={{display: 'inline-block'}}> General Info </h4> 
                  {this.props.match.params.username != localStorage.getItem('username') ? '' :
                    // <button className='btn btn-outline-info btn-profile' > Edit </button>
                    <i className="fas fa-edit" style={{display: 'inline', marginLeft: '1%', marginTop: '-1%', cursor: 'pointer'}} onClick={() => { this.setState({ is_editing: true }) }}></i>
                  }
                </div>
                
                <GeneralInfo username={this.props.match.params.username} is_editing={this.state.is_editing} handle={this.handle_save.bind(this)} />
          </div>
        </div>
        <div className="row">
          <div className="col-md-3">
          </div>
          <div className="col-md-7">
              <h4> Ranking </h4>
                <Ranking username={this.props.match.params.username} />
          </div>
        </div>

      </div>
    );
  }
}

export default Profile;
